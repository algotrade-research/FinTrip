daily_data_query = """
    with price as (
        select o.tickersymbol, o.datetime, o.price as op, c.price as cp, (c.price - o.price) / o.price as ret
        from quote.open o join quote.close c
        on o.tickersymbol = c.tickersymbol and o.datetime = c.datetime and length(o.tickersymbol) = 3
        order by o.datetime, o.tickersymbol
    )

    select extract(year from price.datetime - interval '4 month'), extract(quarter from price.datetime - interval '4 month'),
           price.datetime, price.tickersymbol, price.cp, coalesce(dl.quantity * price.cp, 0)
    from price left outer join quote.dailyvolume dl
    on price.tickersymbol = dl.tickersymbol and price.datetime = dl.datetime
    where price.datetime between %s and %s
    order by price.datetime, price.tickersymbol
"""

financial_info_query = """
    select i.year, i.quarter, i.tickersymbol, i.value, i.code
    from financial.info i
    where i.year between %s and %s and i.code in %s and i.quarter <> 0
    order by i.year, i.quarter, i.tickersymbol, i.code
"""

index_query = """
    select o.datetime, o.price as op, c.price as cp
    from quote.open o join quote.close c
    on o.tickersymbol = c.tickersymbol and o.datetime = c.datetime
    where o.tickersymbol = 'VNINDEX' and o.datetime between %s and %s
    order by o.datetime
"""
