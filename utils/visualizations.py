import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_salary_distribution(df):
    """Create salary distribution chart"""
    fig = px.histogram(
        df,
        x='Monthly Gross Salary (in ZMW)',
        title='Salary Distribution',
        labels={'Monthly Gross Salary (in ZMW)': 'Salary (ZMW)'},
        opacity=0.7
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=10, r=10, t=40, b=20),  # Tighter margins for mobile
        title_x=0.5,  # Center title
        xaxis_title_standoff=10,
        yaxis_title_standoff=10
    )
    return fig

def create_experience_salary_correlation(df):
    """Create experience vs salary scatter plot with trend line"""
    try:
        # Try to create scatter plot with trend line
        fig = px.scatter(
            df,
            x='Years of Experience',
            y='Monthly Gross Salary (in ZMW)',
            title='Experience vs Salary Correlation',
            labels={
                'Years of Experience': 'Experience (Years)',
                'Monthly Gross Salary (in ZMW)': 'Salary (ZMW)'
            },
            trendline="lowess"  # Use lowess instead of ols, more robust
        )
    except Exception as e:
        # Fallback to basic scatter plot without trend line
        fig = px.scatter(
            df,
            x='Years of Experience',
            y='Monthly Gross Salary (in ZMW)',
            title='Experience vs Salary Correlation',
            labels={
                'Years of Experience': 'Experience (Years)',
                'Monthly Gross Salary (in ZMW)': 'Salary (ZMW)'
            }
        )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=40, b=20),
        title_x=0.5,
        xaxis_title_standoff=10,
        yaxis_title_standoff=10
    )
    return fig

def create_industry_salary_box(df):
    """Create box plot of salaries by industry"""
    # Get top 10 industries by count
    top_industries = df['Industry'].value_counts().nlargest(10).index

    # Filter data for top industries
    df_filtered = df[df['Industry'].isin(top_industries)]

    fig = px.box(
        df_filtered,
        x='Industry',
        y='Monthly Gross Salary (in ZMW)',
        title='Salary Ranges by Industry',
        labels={'Monthly Gross Salary (in ZMW)': 'Salary (ZMW)'}
    )
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=40, b=100),  # More bottom margin for labels
        title_x=0.5,
        xaxis_tickangle=-45,  # Angle the industry labels
        showlegend=False
    )
    return fig

def create_degree_distribution(df):
    """Create pie chart of degree distribution with fixed colors.

    Colors:
    - No  -> red
    - Yes -> blue
    """
    # Ensure consistent ordering and labels
    degree_counts = df['Degree'].value_counts()
    counts_df = degree_counts.reset_index()
    counts_df.columns = ['Degree', 'Count']

    fig = px.pie(
        counts_df,
        values='Count',
        names='Degree',
        title='Education Level Distribution',
        color='Degree',
        color_discrete_map={
            'No': 'red',
            'Yes': 'blue',
        },
    )
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=40, b=20),
        title_x=0.5
    )
    return fig

def create_top_roles_salary(df, top_n=10):
    """Create bar chart of average salaries by role"""
    # Calculate average salary by role
    role_avg_salary = df.groupby('Role')['Monthly Gross Salary (in ZMW)'].agg(['mean', 'count'])
    # Get top N roles by count
    top_roles = role_avg_salary.nlargest(top_n, 'count')

    fig = px.bar(
        x=top_roles.index,
        y=top_roles['mean'],
        title=f'Average Salary by Role (Top {top_n} Most Common)',
        labels={
            'x': 'Role',
            'y': 'Average Salary (ZMW)'
        }
    )
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=40, b=100),  # More bottom margin for labels
        title_x=0.5,
        xaxis_tickangle=-45,  # Angle the role labels
        showlegend=False
    )
    return fig