import QtQuick 2.1
import QtQuick.Window 2.0
import QtPositioning 5.5
import QtLocation 5.6

Window {
  id:page
  width: 800
  height: 800
  visible: true

  Map {
    id:myMap
    anchors.fill: parent
    plugin: mapPlugin
    zoomLevel: 17

    property MapCircle circle

    function update(pos) {
      removeMapItem(circle);

      circle = Qt.createQmlObject('import QtLocation 5.3; MapCircle {}', page);
      circle.radius = 30;
      circle.color = "transparent";
      circle.border.color = "red"
      circle.border.width = 3;
      myMap.addMapItem(circle);

      circle.center = pos.coordinate;
      myMap.center = pos.coordinate;

      //console.log("Coordinates: ", pos.coordinate.latitude, pos.coordinate.longitude);
    }
  }

  Plugin {
    id: mapPlugin
    name: "osm"
  }

  PositionSource {
    id: gpsPos
    updateInterval: 500
    active: true
    nmeaSource: "socket://localhost:29999"

    onPositionChanged: {
      myMap.update(position);
    }
  }
}