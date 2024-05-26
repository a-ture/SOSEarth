am5.ready(function() {
  // Create root element
  var root = am5.Root.new("chartdiv");

  // Set themes
  root.setThemes([
    am5themes_Animated.new(root)
  ]);

  // Create the map chart
  var chart = root.container.children.push(am5map.MapChart.new(root, {
    panX: "translateX",
    panY: "translateY",
    projection: am5map.geoMercator()
  }));

  // Create main polygon series for countries
  var polygonSeries = chart.series.push(am5map.MapPolygonSeries.new(root, {
    geoJSON: am5geodata_worldLow,
    exclude: ["AQ"]
  }));

  polygonSeries.mapPolygons.template.setAll({
    tooltipText: "{name}",
    toggleKey: "active",
    interactive: true,
    fill: am5.color(0x007bff) // Set the default fill color (blue in this example)
  });

  // Customize the hover state
  polygonSeries.mapPolygons.template.states.create("hover", {
    fill: am5.color(0xff6f61) // Set the hover color (red in this example)
  });

  // Customize the active state
  polygonSeries.mapPolygons.template.states.create("active", {
    fill: am5.color(0x28a745) // Set the active color (green in this example)
  });

  var previousPolygon;

  polygonSeries.mapPolygons.template.on("active", function(active, target) {
    if (previousPolygon && previousPolygon != target) {
      previousPolygon.set("active", false);
    }
    if (target.get("active")) {
      polygonSeries.zoomToDataItem(target.dataItem);

      // Display country information
      var countryName = target.dataItem.dataContext.name;
      var infoDiv = document.getElementById('infoDiv');
      infoDiv.innerHTML = "<h2>" + countryName + "</h2><p>Additional information about " + countryName + ".</p>";
      infoDiv.style.display = "block";
    } else {
      chart.goHome();
      var infoDiv = document.getElementById('infoDiv');
      infoDiv.style.display = "none"; // Hide the infoDiv when no country is active
    }
    previousPolygon = target;
  });

  // Add zoom control
  var zoomControl = chart.set("zoomControl", am5map.ZoomControl.new(root, {}));
  zoomControl.homeButton.set("visible", true);

  // Set clicking on "water" to zoom out
  chart.chartContainer.get("background").events.on("click", function() {
    chart.goHome();
    var infoDiv = document.getElementById('infoDiv');
    infoDiv.style.display = "none"; // Hide the infoDiv when clicking on water
  });

  // Make stuff animate on load
  chart.appear(1000, 100);
}); // end am5.ready()
