import plotly.express as px

def create_distribution_chart(df, group_col):
    if group_col and group_col in df.columns:
        fig = px.histogram(df, x=group_col, color_discrete_sequence=['indianred'])
        fig.update_layout(
            title=f"{group_col} Distribution",
            xaxis_title=group_col,
            yaxis_title="Count",
            bargap=0.2,
            height=200,
            template='plotly_white'
        )
        return fig
    else:
        return px.histogram()