from django import template
# from system.Encryption import Encryption
register = template.Library()


# @register.simple_tag
# def encode_id(id):
#     return Encryption.encode_id(id)
#
#
# @register.simple_tag
# def decode_id(id):
#     return Encryption.encode_id(id)
#
#
# @register.simple_tag
# def encode(value):
#     return Encryption.encode(value)


@register.simple_tag
def empty_list(lists):
    if len(lists):
        return False
    else:
        return True


@register.simple_tag
def to_list(*args):
    return args



@register.simple_tag
def to_attachment_html(notifc_id):
    return 'Ok its ok'


