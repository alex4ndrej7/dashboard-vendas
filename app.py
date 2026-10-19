
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output

# Carregar a base de dados
df = pd.read_csv("vendas_2020.csv")
df["Data_Pedido"] = pd.to_datetime(df["Data_Pedido"])

# Padronizar o nome do estado de Minas Gerais
df["Estado_Cliente"] = df["Estado_Cliente"].replace({"MINAS": "MG"})

# Nomes dos meses
meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Criar o aplicativo
app = Dash(__name__)
app.title = "Dashboard de Vendas"

# Configuração necessária para a hospedagem
server = app.server


# Criar opções para os filtros
opcoes_mes = [
    {"label": meses[m], "value": m}
    for m in sorted(df["Data_Pedido"].dt.month.unique())
]


def opcoes_coluna(coluna):
    return [
        {"label": valor, "value": valor}
        for valor in sorted(df[coluna].dropna().unique())
    ]


# Montar a página do dashboard
app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "backgroundColor": "#f2f5f9",
        "padding": "25px"
    },
    children=[
        html.H1(
            "Dashboard de Vendas - 2020",
            style={
                "textAlign": "center",
                "color": "#12345a"
            }
        ),

        html.P(
            "Trabalho desenvolvido por Alexandre Araújo e Cauan Etienne",
            style={"textAlign": "center"}
        ),

        html.P(
            "Análise de faturamento, produtos e clientes.",
            style={"textAlign": "center"}
        ),

        html.H3("Filtros de vendas"),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(5, minmax(150px, 1fr))",
                "gap": "12px"
            },
            children=[
                html.Div([
                    html.Label("Mês"),
                    dcc.Dropdown(
                        id="filtro_mes",
                        options=opcoes_mes,
                        placeholder="Todos os meses",
                        clearable=True
                    )
                ]),

                html.Div([
                    html.Label("Representante"),
                    dcc.Dropdown(
                        id="filtro_representante",
                        options=opcoes_coluna("Nome_Representante"),
                        placeholder="Todos",
                        clearable=True
                    )
                ]),

                html.Div([
                    html.Label("Regional"),
                    dcc.Dropdown(
                        id="filtro_regional",
                        options=opcoes_coluna("Regional"),
                        placeholder="Todas",
                        clearable=True
                    )
                ]),

                html.Div([
                    html.Label("Produto"),
                    dcc.Dropdown(
                        id="filtro_produto",
                        options=opcoes_coluna("Nome_Produto"),
                        placeholder="Todos",
                        clearable=True
                    )
                ]),

                html.Div([
                    html.Label("Cliente"),
                    dcc.Dropdown(
                        id="filtro_cliente",
                        options=opcoes_coluna("Nome_Cliente"),
                        placeholder="Todos",
                        clearable=True
                    )
                ])
            ]
        ),

        html.Hr(),

        # Gráficos principais
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(2, minmax(0, 1fr))",
                "gap": "20px"
            },
            children=[
                dcc.Graph(id="grafico_mes"),
                dcc.Graph(id="grafico_representante"),
                dcc.Graph(id="grafico_regional"),
                dcc.Graph(id="grafico_estado")
            ]
        ),

        html.H3("Faturamento por produto"),

        dash_table.DataTable(
            id="tabela_produtos",
            columns=[
                {"name": "Produto", "id": "Produto"},
                {"name": "Faturamento (R$)", "id": "Faturamento"}
            ],
            page_size=10,
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell={
                "padding": "10px",
                "textAlign": "left"
            },
            style_header={
                "backgroundColor": "#12345a",
                "color": "white",
                "fontWeight": "bold"
            }
        ),

        html.Hr(),

        # Filtros encadeados: estado e cidade
        html.H2("Análise por estado e cidade"),

        html.Div([
            html.Label("Selecione o estado"),

            dcc.Dropdown(
                id="filtro_estado",
                options=opcoes_coluna("Estado_Cliente"),
                placeholder="Escolha um estado",
                clearable=True
            )
        ], style={
            "maxWidth": "400px",
            "marginBottom": "15px"
        }),

        html.Div([
            html.Label("Selecione a cidade"),

            dcc.Dropdown(
                id="filtro_cidade",
                placeholder="Escolha uma cidade",
                clearable=True
            )
        ], style={
            "maxWidth": "400px",
            "marginBottom": "15px"
        }),

        dcc.Graph(id="grafico_cidade"),

        html.Hr(),

        html.P(
            "Fonte dos dados: repositório da disciplina Visualização de Dados.",
            style={"textAlign": "center", "color": "#555"}
        ),

        html.P(
            "Desenvolvido por Alexandre Araújo e Cauan Etienne.",
            style={"textAlign": "center", "color": "#555"}
        )
    ]
)


# Atualizar gráficos e tabela conforme os filtros principais
@app.callback(
    Output("grafico_mes", "figure"),
    Output("grafico_representante", "figure"),
    Output("grafico_regional", "figure"),
    Output("grafico_estado", "figure"),
    Output("tabela_produtos", "data"),
    Input("filtro_mes", "value"),
    Input("filtro_representante", "value"),
    Input("filtro_regional", "value"),
    Input("filtro_produto", "value"),
    Input("filtro_cliente", "value")
)
def atualizar_dashboard(mes, representante, regional, produto, cliente):
    dados = df.copy()

    if mes is not None:
        dados = dados[dados["Data_Pedido"].dt.month == mes]

    if representante:
        dados = dados[dados["Nome_Representante"] == representante]

    if regional:
        dados = dados[dados["Regional"] == regional]

    if produto:
        dados = dados[dados["Nome_Produto"] == produto]

    if cliente:
        dados = dados[dados["Nome_Cliente"] == cliente]

    # Faturamento por mês
    por_mes = dados.groupby(
        dados["Data_Pedido"].dt.month
    )["Valor_Total_Venda"].sum().reset_index()

    por_mes.columns = ["Mes", "Faturamento"]
    por_mes["Nome_Mes"] = por_mes["Mes"].map(meses)
    por_mes = por_mes.sort_values("Mes")

    fig_mes = px.line(
        por_mes,
        x="Nome_Mes",
        y="Faturamento",
        markers=True,
        title="Faturamento por mês",
        labels={
            "Nome_Mes": "Mês",
            "Faturamento": "Faturamento (R$)"
        }
    )

    # Faturamento por representante
    por_rep = dados.groupby(
        "Nome_Representante"
    )["Valor_Total_Venda"].sum().reset_index()

    por_rep = por_rep.sort_values(
        "Valor_Total_Venda", ascending=False
    )

    fig_rep = px.bar(
        por_rep,
        x="Valor_Total_Venda",
        y="Nome_Representante",
        orientation="h",
        title="Faturamento por representante",
        labels={
            "Nome_Representante": "Representante",
            "Valor_Total_Venda": "Faturamento (R$)"
        }
    )

    fig_rep.update_layout(yaxis={"categoryorder": "total ascending"})

    # Participação por regional
    por_regional = dados.groupby(
        "Regional"
    )["Valor_Total_Venda"].sum().reset_index()

    fig_regional = px.pie(
        por_regional,
        names="Regional",
        values="Valor_Total_Venda",
        title="Faturamento por regional"
    )

    # Faturamento por estado
    por_estado = dados.groupby(
        "Estado_Cliente"
    )["Valor_Total_Venda"].sum().reset_index()

    por_estado = por_estado.sort_values(
        "Valor_Total_Venda", ascending=False
    )

    fig_estado = px.bar(
        por_estado,
        x="Estado_Cliente",
        y="Valor_Total_Venda",
        title="Faturamento por estado",
        labels={
            "Estado_Cliente": "Estado",
            "Valor_Total_Venda": "Faturamento (R$)"
        }
    )

    # Tabela de faturamento por produto
    por_produto = dados.groupby(
        "Nome_Produto"
    )["Valor_Total_Venda"].sum().reset_index()

    por_produto = por_produto.sort_values(
        "Valor_Total_Venda", ascending=False
    )

    por_produto.columns = ["Produto", "Faturamento"]
    por_produto["Faturamento"] = por_produto["Faturamento"].round(2)

    return (
        fig_mes,
        fig_rep,
        fig_regional,
        fig_estado,
        por_produto.to_dict("records")
    )


# Mostrar somente as cidades do estado selecionado
@app.callback(
    Output("filtro_cidade", "options"),
    Output("filtro_cidade", "value"),
    Input("filtro_estado", "value")
)
def atualizar_cidades(estado):
    if not estado:
        return [], None

    cidades = sorted(
        df.loc[
            df["Estado_Cliente"] == estado,
            "Cidade_Cliente"
        ].dropna().unique()
    )

    opcoes = [
        {"label": cidade, "value": cidade}
        for cidade in cidades
    ]

    return opcoes, None


# Atualizar o gráfico conforme o estado e a cidade escolhidos
@app.callback(
    Output("grafico_cidade", "figure"),
    Input("filtro_estado", "value"),
    Input("filtro_cidade", "value")
)
def atualizar_grafico_cidade(estado, cidade):
    dados = df.copy()

    if estado:
        dados = dados[dados["Estado_Cliente"] == estado]

    if cidade:
        dados = dados[dados["Cidade_Cliente"] == cidade]

    por_cidade = dados.groupby(
        "Cidade_Cliente"
    )["Valor_Total_Venda"].sum().reset_index()

    return px.bar(
        por_cidade,
        x="Cidade_Cliente",
        y="Valor_Total_Venda",
        title="Faturamento por cidade",
        labels={
            "Cidade_Cliente": "Cidade",
            "Valor_Total_Venda": "Faturamento (R$)"
        }
    )


# Iniciar o aplicativo localmente
if __name__ == "__main__":
    app.run(debug=True, port=8050)
