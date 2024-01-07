from django.http import QueryDict


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