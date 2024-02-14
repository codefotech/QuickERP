import json

from django import template
from django.utils.safestring import mark_safe
from django.forms.utils import ErrorDict

register = template.Library()


@register.simple_tag(takes_context=True)
def input(context, name=None, **kwargs):
    className = ''
    data_value = ''
    checked = ''
    data = ''
    field_type = kwargs.get('type')
    if 'class' in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            className = className + classlist

    if 'checked' in kwargs:
        del kwargs['checked']
        checked = 'checked '

    if 'choice_data' in kwargs:
        data = kwargs.get('choice_data')

    error = None
    if context.get('form'):
        if context.get('form').errors:
            if type(context.get('form').errors) == type(ErrorDict()):
                if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                    error = context.get('form').errors.get(str(name))[0]
                    if error:
                        className = className + ' is-invalid'

        if hasattr(context.get('form'), 'data'):
            if context.get('form').data.get(name):
                value = context.get('form').data.get(name)
                data_value = 'value=' + value

        if field_type == 'radio':
            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name) == kwargs.get('choice_data'):
                    checked = 'checked '

    if field_type == 'radio' and 'value' in kwargs:
        if str(kwargs.get('value')) == str(kwargs.get('choice_data')):
            checked = 'checked'
        else:
            checked = ''

    if data:
        data_value = 'value=' + '"' + str(data) + '"'

    attributes = ''.join([f'{key}="{value}"' for key, value in kwargs.items()])
    input_html = f'<input class="{className}" name="{name}" {data_value} {attributes} {checked} >'
    if error:
        input_html = input_html + f'<label class="text-danger input-error">{error if error else " "}</label></br>'
    return mark_safe(input_html)


@register.simple_tag(takes_context=True)
def select(context, options=None, selected=None, name='select', class_list='', id=None, placeholder=None, blank=False,
           **kwargs):
    error = None
    className = ''
    if 'class' in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            className = className + classlist
    # if kwargs.get('multiple'):
    #     name = f"{name}[]"

    if context:
        if context.get('form'):
            if context.get('form').errors:
                if type(context.get('form').errors) == type(ErrorDict()):
                    if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                        error = context.get('form').errors.get(str(name))[0]
                        if error:
                            class_list = class_list + ' is-invalid'

            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name):
                    value = context.get('form').data.get(name)
                    selected = value
    attributes = ''.join([f'{key}="{value}"' for key, value in kwargs.items()])
    select_html = f'<select name="{name}" class="form-control  {class_list}" id={id if id else name} placeholder={placeholder if placeholder else "hfgh"} {attributes}>'
    base_option_html = '' if not blank else '<option value="">Select One</option>'
    if not selected:
        if not kwargs.get('multiple'):
            select_html += base_option_html
    if options:
        for value, label in options.items():
            selected_html = 'selected' if selected is not None and str(value) == str(selected) else ''
            option_html = f'<option value="{str(value)}" {selected_html}>{label}</option>'
            select_html += option_html

    select_html += '</select>'
    if error:
        select_html = select_html + f'<span class="text-danger input-error">{error if error else " "}</span>'

    return mark_safe(select_html)


@register.simple_tag(takes_context=True)
def date(context, name=None, datepicker_type='', class_list='', value=None, **kwargs):
    error = None
    classname = 'form-control inputBox datetimepicker-input '
    date_value = ''
    classname_data = ''
    if 'class' in kwargs:
        class_data = kwargs.get('class')
        del kwargs['class']
        if class_data:
            classname = classname + class_data
    if 'className' in kwargs:
        classname_data = kwargs.get('className')
        del kwargs['className']

    class_list = class_list + '' + classname
    if context:
        if context.get('form'):
            if context.get('form').errors:
                if type(context.get('form').errors) == type(ErrorDict()):
                    if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                        error = context.get('form').errors.get(str(name))[0]
                        if error:
                            class_list = class_list + ' is-invalid'
                    else:
                        class_list = class_list + ' is-valid'

            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name):
                    date_value = context.get('form').data.get(name)

    if value:
        date_value = value
    date_id = 'jid_' + name
    date_picker_id = date_id + '_date_picker'
    attributes = ''.join([f'{key}="{value}"' for key, value in kwargs.items()])

    input_html = f'''
                    <div class="input-group date {datepicker_type} {classname_data}" id="{date_picker_id}" data-target-input="nearest" >
                                                <input type="text" name="{name}" value="{date_value}" class="{class_list}" placeholder="Select from calender" data-target="#{date_picker_id}" id="{date_id}" autocomplete="off">
                                                <div class="input-group-append" data-target="#{date_picker_id}" data-toggle="datetimepicker">
                                                    <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                                                </div>
                    </div>'''
    if error:
        input_html = input_html + f'<span class="text-danger input-error">{error if error else " "}</span>'

    return mark_safe(input_html)


@register.simple_tag(takes_context=True)
def select2(context, options=None, selected=None, name='select', class_list='', id=None, placeholder=None, **kwargs):
    error = None
    className = ''
    if 'class' in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            className = className + classlist
    # if kwargs.get('multiple'):
    #     name = f"{name}[]"

    if context:
        if context.get('form'):
            if context.get('form').errors:
                if type(context.get('form').errors) == type(ErrorDict()):
                    if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                        error = context.get('form').errors.get(str(name))[0]
                        if error:
                            class_list = class_list + ' is-invalid'

            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name):
                    value = context.get('form').data.get(name)
                    selected = value
    attributes = ''.join([f'{key}="{value}"' for key, value in kwargs.items()])
    select_html = f'<select name="{name}" class="form-control {class_list}" id={id if id else name} placeholder={placeholder if placeholder else "hfgh"} {attributes}>'
    base_option_html = '<option value = "">Select One</option>'
    if not selected:
        if not kwargs.get('multiple'):
            select_html += base_option_html
    if options:
        for value, label in options.items():
            selected_html = 'selected' if selected is not None and str(value) in json.dumps(selected) else ''
            option_html = f'<option value="{str(value)}" {selected_html}>{label}</option>'
            select_html += option_html

    select_html += '</select>'
    if error:
        select_html = select_html + f'<span class="text-danger input-error">{error if error else " "}</span>'

    return mark_safe(select_html)


@register.simple_tag(takes_context=True)
def date(context, name=None, datepicker_type='', class_list='', value=None, **kwargs):
    error = None
    classname = 'form-control inputBox datetimepicker-input '
    date_value = ''
    classname_data = ''
    if 'class' in kwargs:
        class_data = kwargs.get('class')
        del kwargs['class']
        if class_data:
            classname = classname + class_data
    if 'className' in kwargs:
        classname_data = kwargs.get('className')
        del kwargs['className']

    class_list = class_list + '' + classname
    if context:
        if context.get('form'):
            if context.get('form').errors:
                if type(context.get('form').errors) == type(ErrorDict()):
                    if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                        error = context.get('form').errors.get(str(name))[0]
                        if error:
                            class_list = class_list + ' is-invalid'
                    else:
                        class_list = class_list + ' is-valid'

            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name):
                    date_value = context.get('form').data.get(name)

    if value:
        date_value = value
    date_id = 'jid_' + name
    date_picker_id = date_id + '_date_picker'
    attributes = ''.join([f'{key}="{value}"' for key, value in kwargs.items()])

    input_html = f'''
                    <div class="input-group date {datepicker_type} {classname_data}" id="{date_picker_id}" data-target-input="nearest" >
                                                <input type="text" name="{name}" value="{date_value}" class="{class_list}" placeholder="Select from calender" data-target="#{date_picker_id}" id="{date_id}" autocomplete="off">
                                                <div class="input-group-append" data-target="#{date_picker_id}" data-toggle="datetimepicker">
                                                    <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                                                </div>
                    </div>'''
    if error:
        input_html = input_html + f'<span class="text-danger input-error">{error if error else " "}</span>'

    return mark_safe(input_html)


@register.simple_tag(takes_context=True)
def gender(context, name, class_list='', value=None, **kwargs):
    error = None
    classname = 'form-control inputBox datetimepicker-input '
    gender_value = ''
    if 'class' in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            classname = classname + classlist

    class_list = class_list + '' + classname
    if context:
        if context.get('form'):
            if context.get('form').errors:
                if type(context.get('form').errors) == type(ErrorDict()):
                    if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                        error = context.get('form').errors.get(str(name))[0]
                        if error:
                            class_list = class_list + ' is-invalid'

            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name):
                    gender_value = context.get('form').data.get(name)

    if value:
        gender_value = value

    input_html = f'''<div><label class="identity_hover">
                                                <input type="radio" name="user_gender" value="Male" {'checked' if gender_value == 'Male' else ''}> Male
                                            </label>
                                            <label class="identity_hover">
                                                <input type="radio" name="user_gender" value="Female" {'checked' if gender_value == 'Female' else ''} > Female
                                            </label>
                                            <label class="identity_hover">
                                                <input type="radio" name="user_gender" value="Not defined" {'checked' if gender_value == 'Not defined' else ''}> Other
                                            </label></div>'''

    if error:
        input_html = input_html + f'<span class="text-danger input-error">{error if error else " "}</span>'

    return mark_safe(input_html)


@register.simple_tag(takes_context=True)
def auto_bill(context, name, class_list='', value=None, **kwargs):
    error = None
    classname = 'form-control inputBox'
    gender_value = ''
    if 'class' in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            classname = classname + classlist

    class_list = class_list + '' + classname
    if context:
        if context.get('form'):
            if context.get('form').errors:
                if type(context.get('form').errors) == type(ErrorDict()):
                    if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                        error = context.get('form').errors.get(str(name))[0]
                        if error:
                            class_list = class_list + ' is-invalid'

            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name):
                    gender_value = context.get('form').data.get(name)

    if value:
        gender_value = str(value)

    input_html = f'''<div><label class="identity_hover">
                                                <input type="radio" name="auto_bill" value="1" {'checked' if gender_value == '1' else ''}>Yes 
                                            </label>
                                            <label class="identity_hover pl-2">
                                                <input type="radio" name="auto_bill" value="0" {'checked' if gender_value == '0' else ''} >No
                                            </label>
                                            </div>'''

    if error:
        input_html = input_html + f'<p class="text-danger input-error">{error if error else " "}</p>'

    return mark_safe(input_html)


@register.simple_tag(takes_context=True)
def billing_type(context, name, class_list='', value=None, **kwargs):
    error = None
    classname = 'form-control inputBox'
    gender_value = ''
    if 'class' in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            classname = classname + classlist

    class_list = class_list + '' + classname
    if context:
        if context.get('form'):
            if context.get('form').errors:
                if type(context.get('form').errors) == type(ErrorDict()):
                    if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                        error = context.get('form').errors.get(str(name))[0]
                        if error:
                            class_list = class_list + ' is-invalid'

            if hasattr(context.get('form'), 'data'):
                if context.get('form').data.get(name):
                    gender_value = context.get('form').data.get(name)

    if value:
        gender_value = value

    input_html = f'''<div><label class="identity_hover">
                                                <input type="radio" name="billing_type" value="1" {'checked' if gender_value == '1' else ''}>Prepaid 
                                            </label>
                                            <label class="identity_hover pl-2">
                                                <input type="radio" name="billing_type" value="2" {'checked' if gender_value == '0' else ''} >Postpaid
                                            </label>
                                            </div>'''

    if error:
        input_html = input_html + f'<p class="text-danger input-error">{error if error else " "}</p>'

    return mark_safe(input_html)


@register.simple_tag(takes_context=True)
def data_time(context, name, datepicker_type='', class_list='', value=None, **kwargs):
    error = None
    classname = 'form-control inputBox datetimepicker-input '
    date_value = ''
    html_class = 'class'
    if html_class in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            classname = classname + classlist

    class_list = class_list + '' + classname
    if context and context.get('form'):
        if context.get('form').errors:
            if type(context.get('form').errors) == type(ErrorDict()):
                if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                    error = context.get('form').errors.get(str(name))[0]
                    if error:
                        class_list = class_list + ' is-invalid'
                else:
                    class_list = class_list + ' is-valid'

        if hasattr(context.get('form'), 'data'):
            if context.get('form').data.get(name):
                date_value = context.get('form').data.get(name)

    if value:
        date_value = value
    date_id = 'jid_' + name
    date_picker_id = date_id + '_date_picker'
    input_html = f'''
    <div aria-label="Datepicker input" role="textbox" aria-multiline="false" aria-disabled="false" aria-readonly="false"><!----><div class="dp__input_wrap"><!----><input class="dp__pointer dp__input_readonly dp__input dp__input_icon_pad dp__input_focus dp__input_reg" placeholder="Select Time" autocomplete="off">
                       <div class="dp__input_wrap"><!----><input class="dp__pointer dp__input_readonly dp__input dp__input_icon_pad dp__input_focus dp__input_reg" placeholder="Select Time" autocomplete="off">
                       
                       
                       <inputname="{name}" value="{date_value}" class="{class_list}" placeholder="Select Time" data-target="#{date_picker_id}" id="{date_id}" autocomplete="off">
                       </div>
                       </div>
                       '''
    if error:
        input_html = input_html + f'<span class="text-danger input-error">{error if error else " "}</span>'

    return mark_safe(input_html)


@register.simple_tag(takes_context=True)
def textarea(context, name=None, value=None, **kwargs):
    className = ''
    data_value = ''
    if 'class' in kwargs:
        classlist = kwargs.get('class')
        del kwargs['class']
        if classlist:
            className = className + classlist

    if 'rows' in kwargs:
        rows = kwargs.get('rows')

    if 'cols' in kwargs:
        cols = kwargs.get('cols')

    error = None
    if context.get('form'):
        if context.get('form').errors:
            if type(context.get('form').errors) == type(ErrorDict()):
                if context.get('form').errors.get(str(name)) and len(context.get('form').errors.get(str(name))) > 0:
                    error = context.get('form').errors.get(str(name))[0]
                    if error:
                        className = className + ' is-invalid'

        if hasattr(context.get('form'), 'data'):
            if context.get('form').data.get(name):
                value = context.get('form').data.get(name)
                data_value = 'value=' + value

    attributes = ''.join([f'{key}="{value}"' for key, value in kwargs.items()])
    textarea_html = f'<textarea class="{className}" name="{name}" rows="{rows}" cols="{cols}" {attributes}> {data_value if not value else value}'
    textarea_html += '</textarea>'

    if error:
        textarea_html = textarea_html + f'<span class="text-danger input-error">{error if error else " "}</span>'
    return mark_safe(textarea_html)
