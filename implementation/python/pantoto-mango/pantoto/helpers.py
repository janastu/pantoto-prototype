from django.conf import settings
import os

def to_form_data(obj):
    data = obj._data
    form_data = {'unicode':unicode(obj)}           
    for field in obj._fields.values():
        if field.type == "ListField" and field.field.type == 'ReferenceField':
            refs = data.get(field.name,[])
            ref_ids = []
            for ref_field in refs:
                ref_ids.append(ref_field.id)
            val = ref_ids
        elif field.type == 'ReferenceField':
            obj = data.get(field.name,None)
            if obj:
                val = obj.id
            else:
                val = None
        else:
            val = data.get(field.name,None)
        if val:
            form_data.update({field.name:val})
    return form_data

def update_obj_from_dict(klass,_dict,_id=None):
    if _id:
        obj = klass.objects.get(id=_id)
    else:
        obj = klass()
    for key,val in _dict.items():
        if hasattr(obj,key):
            setattr(obj,key,val)
    return obj

def handle_uploaded_file(_file):
    dest_dir = os.path.join(settings.UPLOAD_DIR,'user_files')
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    dest_dir = os.path.join(dest_dir,_file.name)
    destination = open(dest_dir, 'wb+')
    for chunk in _file.chunks():
        destination.write(chunk)
    destination.close()
    return (_file.name,_file.name[_file.name.rindex('.')+1:],dest_dir,settings.MEDIA_URL+'uploads/user_files/'+_file.name,_file.size)

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
    return

