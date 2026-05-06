import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def grafico_gastos_por_categoria(df: pd.DataFrame):
    fig = px.bar(
        df.sort_values("total_gastado"),
        x="total_gastado",
        y="categoria",
        orientation="h",
        color="alerta",
        color_discrete_map={True: "#E24B4A", False: "#1D9E75"},
        labels={"total_gastado": "Total ($)", "categoria": ""},
        text="total_gastado"
    )
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=20, t=10, b=0),
        xaxis=dict(showgrid=False, showticklabels=False),
    )
    return fig


def grafico_evolucion_mensual(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["mes"], y=df["ingresos"],
        name="Ingresos", mode="lines+markers",
        line=dict(color="#1D9E75", width=2),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=df["mes"], y=df["gastos"],
        name="Gastos", mode="lines+markers",
        line=dict(color="#E24B4A", width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig