
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
        if relationship.related_model._meta.model_name =='victiminterviewlocationbox':
            related_items_list.append({
                "type": relationship.related_model._meta.model_name,
                "ids": [model.victim_interview_id for model in relationship.related_model.objects.filter(**{relationship.remote_field.name: obj})]
            })
            continue

        related_items_list.append({
            "type": relationship.related_model._meta.model_name,
            "ids": [model.id for model in relationship.related_model.objects.filter(**{relationship.remote_field.name: obj})]
        })

    return related_items_list
