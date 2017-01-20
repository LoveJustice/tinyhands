"""
    This Helper method returns a dictionary of the related items
    to a given object in the following format:
    [{
        "type": "<model_name>",
        "ids": [1,2,3],
    }]
"""
def related_items_helper(self, obj):
    related_items_list = []

    relationships = [
        f for f in obj._meta.get_fields()
        if (f.one_to_many or f.one_to_one)
        and f.auto_created and not f.concrete
    ]

    for relationship in relationships:
        type = relationship.related_model._meta.model_name
        related_items_list.append({
            "type": type,
            "objects": [get_response_object_from_type(type, model) for model in relationship.related_model.objects.filter(**{relationship.remote_field.name: obj})]
        })
    return related_items_list


def get_response_object_from_type(type, object):
    if type == 'address2':
        return {"name": object.name, "id": object.id}
    elif type == 'person':
        return {"name": object.full_name, "id": object.id}
    elif type == 'victiminterviewlocationbox':
        return {"name": object.victim_interview.vif_number, "id": object.victim_interview.id}
    elif type == 'victiminterview':
        return {"name": object.vif_number, "id": object.id}
    return {}