import plotly.express as px
import plotly.graph_objects as go

def make_chart(data=None, type=None, x=None, y=None, z=None, color=None, names=None, values=None, lat=None, lon=None, theta=None, r=None, path=None, text=None, mode=None, title=None):
    if type == 'bar':
        # Gráfico de Barras
        fig = px.bar(data, x=x, y=y, color=color, text=text, title=title)

    elif type == 'line':
        # Gráfico de Linhas
        fig = px.line(data, x=x, y=y, color=color, title=title)

    elif type == 'scatter':
        # Gráfico de Dispersão
        fig = px.scatter(data, x=x, y=y, color=color, text=text, title=title)

    elif type == 'pie':
        # Gráfico de Pizza
        fig = px.pie(data, names=names, values=values, title=title)

    elif type == 'histogram':
        # Histograma
        fig = px.histogram(data, x=x, color=color, title=title)

    elif type == 'area':
        # Gráfico de Área
        fig = px.area(data, x=x, y=y, color=color, title=title)

    elif type == 'box':
        # Gráfico de Caixa
        fig = px.box(data, x=x, y=y, color=color, title=title)

    elif type == 'stacked_bar':
        # Gráfico de Barras Empilhadas
        fig = px.bar(data, x=x, y=y, color=color, text=text, title=title)

    elif type == 'density_heatmap':
        # Mapa de Calor de Densidade
        fig = px.density_heatmap(data, x=x, y=y, color=color, title=title)

    elif type == 'density_contour':
        # Gráfico de Contorno de Densidade
        fig = px.density_contour(data, x=x, y=y, color=color, title=title)

    elif type == 'radar':
        # Gráfico de Radar
        fig = px.line_polar(data, r=r, theta=theta, color=color, title=title)

    elif type == 'polar_bar':
        # Gráfico de Barras Polar
        fig = px.bar_polar(data, r=r, theta=theta, color=color, title=title)

    elif type == 'scatter_geo':
        # Mapa de Dispersão Geoespacial
        fig = px.scatter_geo(data, lat=lat, lon=lon, color=color, title=title)

    elif type == 'choropleth':
        # Choropleth Map
        fig = px.choropleth(data, locations=x, color=color, locationmode='country names', title=title)

    elif type == 'sunburst':
        # Gráfico Sunburst
        fig = px.sunburst(data, path=path, values=values, color=color, title=title)

    elif type == 'treemap':
        # Gráfico Treemap
        fig = px.treemap(data, path=path, values=values, color=color, title=title)

    elif type == 'funnel':
        # Gráfico Funnel
        fig = px.funnel(data, x=x, y=y, color=color, title=title)

    elif type == 'icicle':
        # Gráfico Icicle
        fig = px.icicle(data, path=path, values=values, color=color, title=title)

    elif type == 'multiline':
        # Gráfico de Linhas Multivariável
        fig = px.line(data, x=x, y=y, color=color, title=title)

    elif type == 'scatter_3d':
        # Gráfico de Dispersão 3D
        fig = px.scatter_3d(data, x=x, y=y, z=z, color=color, title=title)

    elif type == 'surface_3d':
        # Gráfico de Superfície 3D
        fig = go.Figure(data=[go.Surface(z=data)])

    elif type == 'waterfall':
        # Waterfall Chart
        fig = go.Figure(go.Waterfall(x=data[x], y=data[y], title=title))

    elif type == 'bullet':
        # Bullet Chart (indicadores de KPI)
        fig = go.Figure(go.Indicator(mode="gauge+number", value=data[y].sum(), title=title))

    elif type == 'line_geo':
        # Mapa de Linhas Geoespacial
        fig = px.line_geo(data, lat=lat, lon=lon, color=color, title=title)

    elif type == 'violin':
        # Gráfico de Violino
        fig = px.violin(data, x=x, y=y, color=color, title=title)

    elif type == 'pareto':
        # Gráfico de Pareto
        fig = px.bar(data, x=x, y=y, text=text).update_traces(textposition='outside')

    else:
        # Tipo não suportado
        raise ValueError(f'Tipo de gráfico "{type}" não é suportado.')

    return fig
