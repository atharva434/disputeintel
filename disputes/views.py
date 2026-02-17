from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import DisputeCase, RiskAnalysis, DisputeChatMessage
from .services import DisputeReasoningAgent
from django.db.models import Count, Q, Case, When, IntegerField, Value
from django.contrib.auth.models import Group, User
import random
from django.utils import timezone

def is_ops_user(user):
    return user.is_staff or user.groups.filter(name='Risk Ops').exists()

@login_required
def customer_dashboard(request):
    cases = DisputeCase.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'disputes/dashboard.html', {'cases': cases})

@user_passes_test(is_ops_user)
def ops_dashboard(request):
    # Sort Logic: CRITICAL(4) > HIGH(3) > MEDIUM(2) > LOW(1)
    # Filter: Show cases assigned to ME, or Critical Unassigned, or High Risk
    
    # 1. Base Query: High Risk OR Assigned to Me OR Critical
    base_qs = DisputeCase.objects.filter(
        Q(analysis__risk_score='High') | 
        Q(assigned_ops=request.user) |
        Q(priority='CRITICAL')
    ).distinct()

    # 2. Annotate with numeric priority
    cases = base_qs.annotate(
        priority_val=Case(
            When(priority='CRITICAL', then=Value(4)),
            When(priority='HIGH', then=Value(3)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('-priority_val', '-created_at')
    
    return render(request, 'disputes/ops_dashboard.html', {'cases': cases})

def assign_specialist(case, classification):
    """
    Finds a group named 'Specialist: <Classification>' and assigns a random member.
    """
    group_name = f"Specialist: {classification}"
    try:
        group = Group.objects.get(name=group_name)
        users = group.user_set.filter(is_active=True)
        if users.exists():
            # Pick one randomly or round-robin (random for MVP)
            specialist = random.choice(list(users))
            case.assigned_ops = specialist
            case.save()
            return specialist
    except Group.DoesNotExist:
        pass
    return None

@login_required
def analyze_dispute(request):
    result = None
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        
        # Save Case
        case = DisputeCase.objects.create(
            customer=request.user,
            description=description,
            amount=amount,
            merchant_category=category,
            status='ANALYZED'
        )
        
        # Run Agent
        agent = DisputeReasoningAgent()
        analysis_json = agent.analyze(description, amount, category)
        
        # Save Analysis
        classification = analysis_json.get('classification', 'Unknown')
        analysis = RiskAnalysis.objects.create(
            case=case,
            risk_score=analysis_json.get('risk_level', 'Unknown'),
            classification=classification,
            fraud_signals=analysis_json.get('fraud_signals', []),
            reasoning_steps=analysis_json.get('reasoning_steps', []),
            recommended_action=analysis_json.get('recommended_action', 'Manual Review'),
            financial_exposure=analysis_json.get('financial_exposure', 'Unknown')
        )
        
        # Auto-Routing Logic
        if analysis.risk_score == 'High' or classification == 'Unauthorized Transaction':
            case.priority = 'CRITICAL'
            case.save()
        
        # Attempt Specialist Assignment
        assign_specialist(case, classification)
        
        return redirect('dispute_result', case_id=case.id)
        
    return render(request, 'disputes/analyze.html')

def dispute_result(request, case_id):
    case = get_object_or_404(DisputeCase, id=case_id)
    # Security check: only allow owner or ops
    if request.user != case.customer and not is_ops_user(request.user):
        return redirect('customer_dashboard')
        
    if request.method == 'POST' and 'message' in request.POST:
        message_text = request.POST.get('message')
        if message_text:
            DisputeChatMessage.objects.create(
                case=case,
                sender=request.user,
                message=message_text,
                is_internal_note=False 
            )
            return redirect('dispute_result', case_id=case.id)
            
    messages = case.messages.all().order_by('created_at')
        
    return render(request, 'disputes/result.html', {'case': case, 'chat_messages': messages})

def insights_dashboard(request):
    if not is_ops_user(request.user):
         return redirect('customer_dashboard')
         
    total_cases = DisputeCase.objects.count()
    high_risk = RiskAnalysis.objects.filter(risk_score='High').count()
    
    # Top Categories
    categories = DisputeCase.objects.values('merchant_category').annotate(total=Count('id')).order_by('-total')[:5]
    
    # Common Classifications
    classifications = RiskAnalysis.objects.values('classification').annotate(total=Count('id')).order_by('-total')[:5]
    
    context = {
        'total_cases': total_cases,
        'high_risk_count': high_risk,
        'categories': categories,
        'classifications': classifications
    }
    return render(request, 'disputes/insights.html', context)
