$(document).ready(function(){
    MB_ATTR = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
            '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="http://mapbox.com">Mapbox</a>';
    MB_URL = 'http://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png';
    var vals = []
    for(var i=0; i < counties_data['features'].length; i++){
        feature = counties_data['features'][i];
        vals.push(feature['properties']['Burglary']);
    }
    var scale = chroma.scale(['blue','red']).domain(vals, 10, 'quantiles');

    function style(feature) {
        return {
            fillOpacity: 0.7,
            fillColor: scale(feature.properties['Burglary']),
            weight: 1,
            opacity: 1,
            color: 'white',
            dashArray: '3',
        };
    }

    var map = L.map('map').setView([37.8, -96], 4);
    L.tileLayer(MB_URL, {attribution: MB_ATTR, id: 'examples.map-i86knfo3'}).addTo(map);
    L.geoJson(counties_data, {style: style}).addTo(map);
})
