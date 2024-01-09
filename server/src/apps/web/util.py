from django.http import QueryDict
from src.other.enums import ProductTypeSlug, ProductType


def combined_qdict(request, kwargs):
    qd = QueryDict(mutable=True)
    for k, v in kwargs.items():
        if type(v) == list:
            for i in v:
                qd.appendlist(k, i)
        else:
            qd[k] = v

    for k in request.GET.keys():
        v = request.GET.getlist(k)
        if not qd.get(k) and v:
            if len(v) > 1:
                for i in v:
                    qd.appendlist(k, i)
            else:
                qd[k] = v[0]
    qd.pop("pathfilter", None)
    return qd


def fmt_float(f):
    s = "%g" % float(f)
    return s.replace(",", ".")


def in_spark(r):
    return r.headers.get("Accept") == "text/html+partial"


def make_similar_url(product):
    from web.path_converter import RimPathParams, SIMILARITY_PARAMS
    slug = ProductTypeSlug[product.type.name].value
    convs = SIMILARITY_PARAMS.get(ProductType.RIMS)
    if not convs:
        return

    url_paths = [f'/{slug}']
    for conv in convs:
        val = getattr(product, conv.filter_name, None)
        if val is None:
            continue
        path = None
        try:
            path = conv.to_url(val)
        except Exception:
            pass
        if path:
            url_paths.append(path)
    return "/".join(url_paths)