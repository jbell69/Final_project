svg.style("background","url('https://www.google.nl/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png') no-repeat");

var complexData = [{
    title: "met1",
    url: "file:///Users/wheeler/Desktop/Screen%20Shot%202020-02-13%20at%209.20.13%20PM.png"
  },
  {
    title: "met2",
    url: "file:///Users/wheeler/Desktop/Screen%20Shot%202020-02-13%20at%209.20.42%20PM.png"
  },
  {
    title: "met3",
    url: "file:///Users/wheeler/Desktop/Screen%20Shot%202020-02-13%20at%209.21.03%20PM.png"
  }
  ];
  
  d3.select(".img-gallery").selectAll("div")
    .data(complexData)
    .enter() // creates placeholder for new data
    .append("div") // appends a div to placeholder
    .classed("col-md-4 thumbnail", true) // sets the class of the new div
    .html(function(d) {
      return `<img src="${d.url}">`;
    }); // sets the html in the div to an image tag with the link
// Load data from department_table.csv
d3.csv("./Resources/department_table.csv").then(function(deptData) {

  console.log(deptData);
})
svg.style("polygon", )


