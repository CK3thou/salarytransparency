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
        opacity=0.8,
        color_discrete_sequence=['#667eea'],
        nbins=30
    )
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white'),
            color='#667eea'
        ),
        hovertemplate='<b>Salary Range</b>: %{x:$,.0f}<br>' +
                      '<b>Count</b>: %{y}<extra></extra>'
    )
    fig.update_layout(
        showlegend=False,
        height=450,
        margin=dict(l=50, r=20, t=60, b=50),
        title_x=0.5,
        title_font=dict(size=20, color='#2d3748', family='Inter'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=12, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=12, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        xaxis_title_standoff=15,
        yaxis_title_standoff=15
    )
    return fig

def create_experience_salary_correlation(df):
    """Create experience vs salary scatter plot with trend line (uses USD when available)."""
    col, label = _pick_salary_column(df)
    df = df.copy()
    df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Years of Experience'] = pd.to_numeric(df['Years of Experience'], errors='coerce')
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
            trendline="lowess",  # Use lowess instead of ols, more robust
            color_discrete_sequence=['#764ba2'],
            opacity=0.6
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
            },
            color_discrete_sequence=['#764ba2'],
            opacity=0.6
        )

    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(width=1, color='white'),
            color='#764ba2'
        ),
        hovertemplate='<b>Experience</b>: %{x} years<br>' +
                      '<b>Salary</b>: %{y:$,.0f}<extra></extra>'
    )
    
    # Update trendline color if it exists
    if len(fig.data) > 1:
        fig.data[1].update(
            line=dict(color='#667eea', width=3),
            name='Trend'
        )
    
    fig.update_layout(
        height=450,
        margin=dict(l=50, r=20, t=60, b=50),
        title_x=0.5,
        title_font=dict(size=20, color='#2d3748', family='Inter'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=12, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=12, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        xaxis_title_standoff=15,
        yaxis_title_standoff=15
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
        labels={col: label},
        color_discrete_sequence=['#667eea']
    )
    fig.update_traces(
        marker=dict(color='#764ba2', size=4),
        line=dict(color='#667eea', width=2),
        fillcolor='rgba(102, 126, 234, 0.3)',
        hovertemplate='<b>Industry</b>: %{x}<br>' +
                      '<b>Salary</b>: %{y:$,.0f}<extra></extra>'
    )
    fig.update_layout(
        height=550,
        margin=dict(l=50, r=20, t=60, b=120),
        title_x=0.5,
        title_font=dict(size=20, color='#2d3748', family='Inter'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=11, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=12, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        xaxis_tickangle=-45,
        showlegend=False
    )
    return fig

def create_degree_distribution(df):
    """Create pie chart of degree distribution with modern colors."""
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
            'No': '#f56565',
            'Yes': '#667eea',
        },
        hole=0.4  # Donut chart style
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>' +
                      'Count: %{value}<br>' +
                      'Percentage: %{percent}<extra></extra>'
    )
    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
        title_x=0.5,
        title_font=dict(size=20, color='#2d3748', family='Inter'),
        font=dict(size=12, color='#4a5568', family='Inter'),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=12, color='#4a5568')
        )
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

    # Create a DataFrame for the bar chart
    bar_df = pd.DataFrame({
        'Role': top_roles.index,
        'Average Salary': top_roles['mean']
    })
    
    fig = px.bar(
        bar_df,
        x='Role',
        y='Average Salary',
        title=f'Average Salary by Role (Top {top_n} Most Common)',
        labels={
            'Role': 'Role',
            'Average Salary': f'Average {label}'
        },
        color='Average Salary',
        color_continuous_scale='Viridis'
    )
    fig.update_traces(
        marker=dict(
            line=dict(color='white', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>' +
                      '<b>Average Salary</b>: %{y:$,.0f}<extra></extra>'
    )
    fig.update_layout(
        height=550,
        margin=dict(l=50, r=20, t=60, b=120),
        title_x=0.5,
        title_font=dict(size=20, color='#2d3748', family='Inter'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=11, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=False
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#4a5568'),
            tickfont=dict(size=12, color='#718096'),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        xaxis_tickangle=-45,
        showlegend=False,
        coloraxis_showscale=False
    )
    return fig