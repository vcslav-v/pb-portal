from pb_portal import connectors


def get_flat_cat(cattegory: connectors.finam.schemas.Node) -> dict:
    flat_cat: dict = {}
    flat_cat[cattegory.id] = []
    for child in cattegory.children:
        flat_cat[cattegory.id].append([child.id, child.name])
        flat_cat.update(get_flat_cat(child))
    return flat_cat


def get_youngest_child(ids: list[int], cattegory: connectors.finam.schemas.Node):
    if len(ids) == 1:
        return ids[0]
    l_ids = ids.copy()
    for child in cattegory.children:
        if child.id in l_ids:
            l_ids.remove(child.id)
            return get_youngest_child(l_ids, child)
