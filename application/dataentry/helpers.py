"""
    This Helper method returns a dictionary of the related items
    to a given object in the following format:
    [{
        "type": "<model_name>",
        "ids": [1,2,3],
    }]

    Currently this is only used for serializing addresses related items
    but it could be extended to work on other model types as well
"""


def related_items_helper(self, obj):
    related_items_list = []

    relationships = [
        f for f in obj._meta.get_fields()
        if (f.one_to_many or f.one_to_one)
        and f.auto_created and not f.concrete
    ]

    for relationship in relationships:
        model_type = relationship.related_model._meta.model_name
        related_items_list.append({
            "type": model_type,
            "objects": [get_response_object_from_model_type(model_type, model) for model in relationship.related_model.objects.filter(**{relationship.remote_field.name: obj})]
        })
    return related_items_list


def get_response_object_from_model_type(model_type, instance):
    if model_type == 'address2':
        return {"name": instance.name, "id": instance.id}
    elif model_type == 'person':
        return {"name": instance.full_name, "id": instance.id}
    elif model_type == 'victiminterviewlocationbox':
        return {"name": instance.victim_interview.vif_number, "id": instance.victim_interview.id}
    elif model_type == 'victiminterview':
        return {"name": instance.vif_number, "id": instance.id}
    return {}
