from django import template

register = template.Library()

@register.filter
def getitem(dictionary, key):
    return dictionary.get(key)


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def filter_exam(marks_queryset, exam):
    return marks_queryset.filter(exam=exam).select_related('subject')

@register.filter
def get_subject_mark(marks_queryset, subject):
    return marks_queryset.filter(subject=subject).first()

@register.filter
def filter_passed(results):
    return [r for r in results if r.is_pass]

@register.filter
def filter_failed(results):
    return [r for r in results if not r.is_pass]

@register.filter
def subtract(value, arg):
    return value - arg

@register.simple_tag
def get_rank_class(rank):
    if rank == 1:
        return 'rank-1'
    elif rank == 2:
        return 'rank-2'
    elif rank == 3:
        return 'rank-3'
    return ''

@register.filter
def average_pass(exam_data):
    if not exam_data:
        return 0
    total = sum(d['pass_percentage'] for d in exam_data)
    return round(total / len(exam_data), 1)

@register.filter
def average_percentage(exam_data):
    if not exam_data:
        return 0
    total = sum(d['avg_percentage'] for d in exam_data)
    return round(total / len(exam_data), 1)

@register.filter
def best_exam(exam_data):
    if not exam_data:
        return "N/A"
    best = max(exam_data, key=lambda x: x['avg_percentage'])
    return best['exam'].name

@register.filter
def best_exam_avg(exam_data):
    if not exam_data:
        return 0
    best = max(exam_data, key=lambda x: x['avg_percentage'])
    return best['avg_percentage']

@register.filter
def worst_exam(exam_data):
    if not exam_data:
        return "N/A"
    worst = min(exam_data, key=lambda x: x['avg_percentage'])
    return worst['exam'].name

@register.filter
def worst_exam_avg(exam_data):
    if not exam_data:
        return 0
    worst = min(exam_data, key=lambda x: x['avg_percentage'])
    return worst['avg_percentage']

@register.filter
def trend(exam_data):
    if len(exam_data) < 2:
        return "Insufficient data"
    first = exam_data[0]['avg_percentage']
    last = exam_data[-1]['avg_percentage']
    if last > first + 5:
        return "Improving ↗"
    elif last < first - 5:
        return "Declining ↘"
    else:
        return "Stable →"

@register.filter
def highest_pass(exam_analysis):
    if not exam_analysis:
        return "N/A"
    highest = max(exam_analysis, key=lambda x: x['pass_percentage'])
    return highest['exam'].name

@register.filter
def highest_pass_val(exam_analysis):
    if not exam_analysis:
        return 0
    highest = max(exam_analysis, key=lambda x: x['pass_percentage'])
    return highest['pass_percentage']

@register.filter
def lowest_pass(exam_analysis):
    if not exam_analysis:
        return "N/A"
    lowest = min(exam_analysis, key=lambda x: x['pass_percentage'])
    return lowest['exam'].name

@register.filter
def lowest_pass_val(exam_analysis):
    if not exam_analysis:
        return 0
    lowest = min(exam_analysis, key=lambda x: x['pass_percentage'])
    return lowest['pass_percentage']

@register.filter
def highest_avg(exam_analysis):
    if not exam_analysis:
        return "N/A"
    highest = max(exam_analysis, key=lambda x: x['avg_marks'] if x['avg_marks'] else 0)
    return highest['exam'].name

@register.filter
def highest_avg_val(exam_analysis):
    if not exam_analysis:
        return 0
    highest = max(exam_analysis, key=lambda x: x['avg_marks'] if x['avg_marks'] else 0)
    return highest['avg_marks']

@register.filter
def subject_trend(exam_analysis):
    if len(exam_analysis) < 2:
        return "Insufficient data"
    valid_data = [x for x in exam_analysis if x['avg_marks'] is not None]
    if len(valid_data) < 2:
        return "Insufficient data"
    first = valid_data[0]['avg_marks']
    last = valid_data[-1]['avg_marks']
    if last > first + 2:
        return "Improving ↗"
    elif last < first - 2:
        return "Declining ↘"
    else:
        return "Stable →"