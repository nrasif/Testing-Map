import pandas as pd
import numpy as np
import folium
from folium import plugins
from folium.plugins import Search

import lasio
import os
import glob
import webbrowser
import plotly.graph_objects as go
from plotly.subplots import make_subplots


#A blank layer map with coordinate center in Aceh
map1 = folium.Map(location=[4.695135,96.749397], zoom_start=8, control_scale=300, tiles=None)

#Put ESRI Satellite for the layer map
tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = False
       ).add_to(map1)

# put a minimap on bottom corner of the main map (optional, can be turned off)
minimap = plugins.MiniMap(toggle_display=True)
map1.add_child(minimap)
plugins.ScrollZoomToggler().add_to(map1)
plugins.Fullscreen(position="topright").add_to(map1)

#Calling all blocks
all_blocks = folium.FeatureGroup(name='All Blocks')
map1.add_child(all_blocks)

#BlockA with default style
BlockA = plugins.FeatureGroupSubGroup(all_blocks, 'Block A')
map1.add_child(BlockA)

#BlockB
BlockB = plugins.FeatureGroupSubGroup(all_blocks, 'Block B')
map1.add_child(BlockB)

#BlockC with different color style (testing feature)
style1 = {'fillColor': '#e6db4c', 'color': '#e6db4c'}
BlockC = plugins.FeatureGroupSubGroup(all_blocks, 'Block C')
map1.add_child(BlockC)

#popup testing table
table_html = '''

<!DOCTYPE html>
<html>
<center> <table style="height: 126px; width: 305px;">
<tbody>
<tr>
<td style="background-color: #e6db4c;"><span style="color: #000000;">Working Area </span></td>
<td style="width: 150px;background-color: #f2f9ff;"><span style="color: #000000;">Testing 1 </span></td>
</tr>
<tr>
<td style="background-color: #e6db4c;"><span style="color: #000000;">Operator </span></td>
<td style="width: 150px;background-color: #f2f9ff;"><span style="color: #000000;">Testing 2 </span></td>
</tr>
<tr>
<td style="background-color: #e6db4c;"><span style="color: #000000;">Status </span></td>
<td style="width: 150px;background-color: #f2f9ff;"><span style="color: #000000;">Production </span></td>
</tr>
</tbody>
</table></center>

<center><a href="testing_123.html">Open General Information</a>

</html>

'''
# pull in geojson layers and add to map
folium.GeoJson(r'templates\GeoJSON_Blocks_Examples\BlockA.geojson', name='Block A').add_to(BlockA)
folium.GeoJson(r'templates\GeoJSON_Blocks_Examples\BlockB.geojson', name='Block B').add_to(BlockB)
folium.GeoJson(r'templates\GeoJSON_Blocks_Examples\BlockC.geojson', name='Block C', 
               style_function=lambda x:style1, 
               tooltip='Click for further information').add_to(BlockC).add_child(folium.Popup(folium.Html(table_html, script=True),
                                                                                             max_width=500))


## Popup using only text
# folium.GeoJson('BlockC.geojson', 
#                style_function=lambda x:style1, 
#                tooltip='Click for further information').add_to(BlockC).add_child(folium.Popup('Testing popup feature', 
#                                                                                                        max_width=300,
#                                                                                                       min_width=300))

# add layer control to map (allows layers to be turned on or off)
folium.LayerControl(collapsed=False).add_to(map1)


#Read all the well log data
paths = sorted(glob.glob(os.path.join("well_contoh", "*.LAS")))
well_df = [0]*2
for i in range(len(paths)):
    well = lasio.read(paths[i])
    df = well.df()
    well_df[i] = df.reset_index()
well1, well2 = well_df #only 2 wells


#Automatic well log plots if any well log data comes in in the future
html_list = []
dataframe_well = {'Well1F':well1, 'Well2F':well2} #defining dataframe

wells = ['Well1F','Well2F'] #list of well for looping

#list of longitude and latitude for well 1 and well 2 respectively (a dummy coordinate)
Longitude = [96.083956, 96.356427]
Latitude = [5.456862, 5.328133]

#list of logs and their colors
logs = ['CALI', 'GR', 'RT', 'NPHI', 'RHOB']
colors = ['black', 'green', 'red', 'royalblue', 'mediumaquamarine']

#plot
log_cols = np.arange(1,8)
logplot = make_subplots(rows=1, cols=len(logs), shared_yaxes = True, specs=[[{},{},{},{},{}]], 
                        horizontal_spacing=0.005)

for i in range(len(wells)):
    for j in range(len(logs)):
        if j == 2: #change to log for RT
            logplot.add_trace(go.Scatter(
                x=dataframe_well[wells[i]][logs[j]], 
                y=dataframe_well[wells[i]]['DEPTH'], 
                name=logs[j], 
                line_color=colors[j]), 
                              row=1, col=log_cols[j])
            logplot.update_xaxes(type='log', row=1, col=log_cols[j], title_text=logs[j], tickfont_size=12, linecolor='#585858')
        else:
            logplot.add_trace(go.Scatter(
                x=dataframe_well[wells[i]][logs[j]],
                y=dataframe_well[wells[i]]['DEPTH'], 
                name=logs[j], 
                line_color=colors[j]), row=1, col=log_cols[j])
            logplot.update_xaxes(col=log_cols[j], title_text=logs[j], linecolor='#585858')
    
    logplot.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, ticks='inside', tickangle=45)
    logplot.update_yaxes(tickmode='linear', tick0=0, dtick=250, showline=True, linewidth=2, ticks='outside', mirror=True, linecolor='black')
    logplot.update_yaxes(row=1, col=1, autorange='reversed')
    logplot.update_layout(height=700, width=700, showlegend=False)
    logplot.update_layout(
                 title_text="Example of " + '<b>' + str(wells[i]) + '</b>', #Add a chart title
                 title_font_family="Arial",
                 title_font_size = 25, title_x=0.5)

    logplot.write_html(r'templates\Well_Log_Plotly\fig'+str(wells[i])+'.html') # the plot is automatically saved as html

    #list html plots to show what pop up folium should show on the map
    html_list.append('fig'+str(wells[i])+'.html')

#make a dataframe which is used for plotting the well head point in folium
df_point = pd.DataFrame(list(zip(wells, html_list, Longitude, Latitude)), columns =['Well_Name', 'HTML_list', 'Longitude', 'Latitude'])

#Start plotting well head in map with well log plot as a pop up widget
for i in range(0,len(df_point)):
    html="""
    <iframe src=\""""  '../templates/Well_Log_Plotly/' + df_point['HTML_list'][i] + """\" width="700" height="800"  frameborder="0">    
    """

    popup = folium.Popup(folium.Html(html, script=True))
    
#     #Cirlce marker ver.
#     folium.CircleMarker([df_point['Latitude'].iloc[i],df_point['Longitude'].iloc[i]],
#                         popup=popup,radius=3.5,opacity=1,color='#ccd132').add_to(map1)
    
    #Marker with icon ver.
    folium.Marker([df_point['Latitude'].iloc[i],df_point['Longitude'].iloc[i]],
                  popup=popup,icon=folium.Icon( icon='glyphicon-pushpin')).add_to(map1)

blocksearch = Search(
    layer=all_blocks,
    search_label="name",
    placeholder='Search...',
    collapsed=False
).add_to(map1)
    
map1.save(r"templates\testing_map.html")

# webbrowser.open(r'templates\testing_map.html')