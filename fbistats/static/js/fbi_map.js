$(document).ready(function(){
    MB_ATTR = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
            '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="http://mapbox.com">Mapbox</a>';
    MB_URL = 'http://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png';

    function getColor(i){
        if (i < 0.05){
            scale = chroma.scale(['blue', 'green', 'yellow', 'orange', 'red']).domain([0.0,0.05]).out('hex');
            return scale(i);
        }
        else{
            return '#ff0000';
        }
    }

    function style(feature) {
        return {
            fillOpacity: 0.7,
            fillColor: getColor(feature.properties['Forcible rape']),
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
