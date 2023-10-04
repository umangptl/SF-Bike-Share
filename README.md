# Bay Area Bike Share Data Visualization
This Streamlit app provides visualizations and comparisons of Bay Area bike share data using Google BigQuery as the data source.
- Streamlit - https://umangptl-cmpe-255-a1.streamlit.app/
<p>
<img width="500" alt="screenshot" src="https://github.com/umangptl/SF-Bike-Share/blob/main/Screenshot.png">
<img width="500" alt="screenshot" src="https://github.com/umangptl/SF-Bike-Share/blob/main/Screenshot3.png">
<img width="500" alt="screenshot" src="https://github.com/umangptl/SF-Bike-Share/blob/main/Screenshot1.png">
<img width="500" alt="screenshot" src="https://github.com/umangptl/SF-Bike-Share/blob/main/Screenshot2.png">
</p>

## Features
### Geo Visualization
- Visualize bike share data on interactive maps.
- Explore different time slices and rush hours using sliders.
- View hexagon maps and ride distribution histograms.
  
### Date Comparison
- Compare bike trips over different time frames, including per date, per month, per week, and per day.
- Visualize the number of rides using bar charts.

### Start Station Comparison
- Visualize the top 15 start stations with the most trip counts.
- Select and compare multiple start stations to see the number of trips.

### Data Source
- The app uses Google BigQuery as the data source, specifically the bigquery-public-data.san_francisco_bikeshare data

## Technology Requirements
- Pandas
- Streamlit
- Pydeck
- Numpy
- Altair
- Google cloud BigQuery
- Google Auth 
