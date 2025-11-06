import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def _pick_salary_column(df: pd.DataFrame) -> tuple[str, str]:
    """Return (column_name, pretty_label) for salary.
    Prefer 'Monthly Salary in USD' when available; otherwise fall back to 'Monthly Gross Salary'.
    """
    if 'Monthly Salary in USD' in df.columns:
        # Use USD if the column exists and has any non-null numeric values; else fallback
        try:
            s = pd.to_numeric(df['Monthly Salary in USD'], errors='coerce')
            if s.notna().sum() > 0:
                return 'Monthly Salary in USD', 'Salary (USD)'
        except Exception:
            pass
    return 'Monthly Gross Salary', 'Salary'

def create_salary_distribution(df):
    """Create salary distribution chart (uses USD when available)."""
    col, label = _pick_salary_column(df)
    # ensure numeric
    df = df.copy()
    df[col] = pd.to_numeric(df[col], errors='coerce')
    fig = px.histogram(
        df,
        x=col,
        title='Salary Distribution',
        labels={col: label},
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
    """Create experience vs salary scatter plot with trend line (uses USD when available)."""
    col, label = _pick_salary_column(df)
    df = df.copy()
    df[col] = pd.to_numeric(df[col], errors='coerce')
    try:
        # Try to create scatter plot with trend line
        fig = px.scatter(
            df,
            x='Years of Experience',
            y=col,
            title='Experience vs Salary Correlation',
            labels={
                'Years of Experience': 'Experience (Years)',
                col: label
            },
            trendline="lowess"  # Use lowess instead of ols, more robust
        )
    except Exception as e:
        # Fallback to basic scatter plot without trend line
        fig = px.scatter(
            df,
            x='Years of Experience',
            y=col,
            title='Experience vs Salary Correlation',
            labels={
                'Years of Experience': 'Experience (Years)',
                col: label
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
    """Create box plot of salaries by industry (uses USD when available)."""
    col, label = _pick_salary_column(df)
    df = df.copy()
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # Get top 10 industries by count
    top_industries = df['Industry'].value_counts().nlargest(10).index

    # Filter data for top industries
    df_filtered = df[df['Industry'].isin(top_industries)]

    fig = px.box(
        df_filtered,
        x='Industry',
        y=col,
        title='Salary Ranges by Industry',
        labels={col: label}
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
    """Create bar chart of average salaries by role (uses USD when available)."""
    col, label = _pick_salary_column(df)
    # Calculate average salary by role
    role_avg_salary = df.copy()
    role_avg_salary[col] = pd.to_numeric(role_avg_salary[col], errors='coerce')
    role_avg_salary = role_avg_salary.groupby('Role')[col].agg(['mean', 'count'])
    # Get top N roles by count
    top_roles = role_avg_salary.nlargest(top_n, 'count')

    fig = px.bar(
        x=top_roles.index,
        y=top_roles['mean'],
        title=f'Average Salary by Role (Top {top_n} Most Common)',
        labels={
            'x': 'Role',
            'y': f'Average {label}'
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