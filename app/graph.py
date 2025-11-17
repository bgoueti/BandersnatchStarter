from altair import Chart
from pandas import DataFrame
import altair as alt
import pandas as pd 


def chart(df: DataFrame, x, y, target) -> Chart:
    '''
    Build a scatter plot with points colored by 'target'.
    - df: DataFrame containing at least columns x, y, target.
    - x, y: culumn named for for axes (numeric recommended).
    - target: column name used for color (categorical).
    Returns:
        altair.Chart object.
    '''
    
    if df is None or df.empty:
        # Return an empty chart if no data 
        return alt.Chart(pd.DataFrame({x: [], y: [], target: []})).mark_point()   
    
    # Ensure expected columns exist, otherwise attempt to proceed gracefully.
    for col in (x, y, target):
        if col not in df.columns:
            df[col] = None
            
    # Build chart: points with tooltip and color by target
    base = alt.Chart(df).mark_point(filled=True, size=60).encode(
        x=alt.X(x, title=x),
        y=alt.Y(y, title=y),
        color=alt.Color(target, title=target),
        tooltip=[x, y, target]
    ).properties(
            width=600,
            height=400,
            title=f"{y} vs {x} (colored by {target})"
        ).interactive()
    
    return base