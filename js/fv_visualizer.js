$(function(){
$('#filter').submit(function () {
    var inputs = $('#filter :input');
    var values = {};
    inputs.each(function() {
        values[this.name] = $(this).val();
    });
    console.log(values['data']);
    $.ajax({
        type: 'POST',
        url: 'http://localhost:8000/filter',
        cache: false,
        data : { 'filter' : values['data']},
        dataType : 'json',
        success: function(json) {
            return true;
        }
            });
        return false;
        });
});


function getHTML(data) {
    var items = [];
    $.each(data['rib'], function(obj) {
        items.push('<li>Prefix: ' + data['rib'][obj]['prefix'] + ' -> nextHop: ' + data['rib'][obj]['nexthop'] +  '</li>');
    });

    return $('<ul/>', {
         html: items.join('')
    });
}

function setTipsy(tag, data_source) {
    $(tag + ' svg image').tipsy({ 
          //trigger: 'manual',
          gravity: $.fn.tipsy.autoNS,
          html: true, 
          fade: true,
          /*title: function(){
                return  $(this).attr('id');
            },*/
          title: function () {
            var ret = "";
            var name = $(this).attr('id');
            if (name.indexOf("SDNBGP1") != -1) {
                 $.ajax({
                    url: data_source + '/bgp1',
                    dataType: 'json',
                    async: false,
                    success:  function (data) {
                        ret = getHTML(data);
            
                    }
                });
                return ret.html();
                
            } else if (name.indexOf("SDNBGP2") != -1) {
                 $.ajax({
                    url: data_source + '/bgp2',
                    dataType: 'json',
                    async: false,
                    success:  function (data) {
                        ret = getHTML(data);

                    }
                });
                return ret.html();

            }  
            else {
                return name
            }
          }   
    });   
}

function reset() {

    $(".spinner").hide();

}

function getFlows(data_source, tag, dpid) {
    var ret;
    $.ajax({
                    url: data_source + '/flowtable/'+dpid,
                    dataType: 'json',
                    async: true,
                    success:  function (data) {
                        console.log(data);
                        drawTree(data, true)
                        //d3.select(tag).text(JSON.stringify(data, null, "  "));
                    }
    });
}
    
    

function setRegularLayout(){
  var layout = {};
  layout['SDNBGP1'] = [3/10, 1/10];
  layout['SDNBGP2'] = [9/10, 1/10]; 
  layout['FloodLight-1'] = [1/10, 1/10];
  layout['FloodLight-2'] = [7/10, 1/10];
  layout['00:00:00:00:00:00:00:a1'] = [1/10, 2/5];
  layout['00:00:00:00:00:00:00:a2'] = [1/10, 4/5];
  layout['00:00:00:00:00:00:00:a3'] = [2/10, 3/5];
  layout['00:00:00:00:00:00:00:a4'] = [3/10, 2/5];
  layout['00:00:00:00:00:00:00:a5'] = [3/10, 4/5];
  
  layout['AS1'] = [5/10, 2/5];
  layout['AS2'] = [4/10, 4/5];
  layout['AS3'] = [6/10, 4/5];

  layout['00:00:00:00:00:00:00:b1'] = [9/10, 2/5];
  layout['00:00:00:00:00:00:00:b2'] = [9/10, 4/5];
  layout['00:00:00:00:00:00:00:b3'] = [8/10, 3/5];
  layout['00:00:00:00:00:00:00:b4'] = [7/10, 2/5];
  layout['00:00:00:00:00:00:00:b5'] = [7/10, 4/5];

  layout['00:00:00:00:00:00:0a:31'] = [1/20, 1/5];
  layout['00:00:00:00:00:00:0a:32'] = [1/20, 3/5];
  layout['00:00:00:00:00:00:0a:33'] = [4/20, 1/5];
  layout['00:00:00:00:00:00:0a:34'] = [4/20, 3/5];
  return layout;
}

var layout = setRegularLayout();

var m = [10, 60, 10, 60],
    tw = 1280 - m[1] - m[3],
    th = 400 - m[0] - m[2],
    i = 0,
    root, vis;

var tree = d3.layout.tree()
    .size([th, tw]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

function start_demo(data_source, tag, fl_tag) {


    var h = 800, w = 1200;//window.innerHeight - 150, w = window.innerWidth - 100;        
    var image_size = 100;
    var fill = d3.scale.category10();
    var pfill = d3.scale.category20();

    vis = d3.select(fl_tag).append("svg:svg")
    .attr("width", tw + m[1] + m[3])
    .attr("height", th + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");



    var svg = d3.select(tag).append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    d3.json(data_source + '/topology', draw);
    
    setTimeout("setTipsy(\'"+tag+"\',\'"+data_source+"\')", 3000); 
 
    function draw(json) {

      var bgp_nodes = [ { "name" : "SDNBGP1", "group" : "0" }, { "name" : "SDNBGP2", "group" : "1" }, { "name" : "FloodLight-1", "group" : "0" }, { "name" : "FloodLight-2", "group" : "1" } ];

      var nodes = json.nodes.map(Object);
    
      var groups = d3.nest().key(function(d) { return d.group; }).entries(nodes);
      
      var bgp_groups = d3.nest().key(function(d) { return d.group; }).entries(bgp_nodes);  
      
      var groupPath = function(d) {
        return "M" + 
        d3.geom.hull(d.values.map(function(i) {
                if (i.name.indexOf("a1") != -1) {
                    return [i.x, i.y ];
                }
                if (i.name.indexOf("a2") != -1) {
                    return [i.x, i.y + image_size];
                }
                if (i.name.indexOf("b1") != -1) {
                    return [i.x + image_size, i.y ];
                }
                 if (i.name.indexOf("b2") != -1) {
                    return [i.x + image_size, i.y + image_size ];
                }
                return [i.x + image_size/2, i.y + image_size / 2]; }))
            .join("L")
        + "Z";
    };

    var bgp_groupPath = function(d) {
        var ret = "M"
        for (var i = 0 ; i < d.values.length ; i++) {
            if (i !== d.values.length -1) {
                ret = ret + (w*layout[d.values[i].name][0] + image_size/2) + "," +  h*layout[d.values[i].name][1] ;
                ret = ret + "L";
            } else {
                ret = ret + (w*layout[d.values[i].name][0] - image_size/2) + "," +  h*layout[d.values[i].name][1] ;
            }
        }
        return ret +"Z";

    };

    var groupFill = function(d, i) { return fill(i & 3); };
    
          var force = d3.layout.force()
                .gravity(0)
                .linkDistance(10)
                .linkStrength(0)
                .charge(0)
                .size([w, h])
                .nodes(nodes)
                .links(json.links).start()


    
      var link = svg.selectAll("line")
          .data(json.links)
         .enter().append("svg:line")
          .attr("stroke","green")
          .attr("stroke-width",2)
          .attr("id", function(d){return d.id;});

      var node = svg.selectAll("g.node")
          .data(nodes)
        .enter().append("svg:g")
          .attr("class", "node")
         .append("svg:image")
          .attr("xlink:href", function(d) {if (d.name.indexOf("AS") != -1) { return "images/cloud.png"; } else { return  "images/router.png"; } } )
          .attr("width", image_size + "px")
          .attr("height", image_size + "px")
          .attr("id", function(d){ 
                 if (d.name.indexOf("AS") != -1) { 
                    return d.name; 
                 } else { 
                    return d.name.split(":").pop();
                 }
          })
          .on("click", function(d) { getFlows(data_source, fl_tag, d.name); })
        .call(force.drag);

      var bgp_node = svg.selectAll("node")
          .data(bgp_nodes)
        .enter().append("svg:g")
          .attr("class", "node")
          .append("svg:image") 
          .attr("xlink:href", function(d) {if (d.name.indexOf("FloodLight") != -1) { return "images/floodlight.png"; } else { return  "images/bgpd.png";  }} )
          .attr("width", function (d) { if (d.name.indexOf("FloodLight") != -1) { return 2*image_size + "px"; } else { return  image_size + "px";  }})
          .attr("height", image_size + "px")
          .attr("x", function(d) { return (w * layout[d.name][0]) - image_size/2; } )
          .attr("y", function(d) { return (h * layout[d.name][1]) - image_size/2; } )
          .attr("id", function(d){return d.name;})



    svg.style("opacity", 1e-6)
  .transition()
    .duration(1000)
    .style("opacity", 1);

      force
        .on("tick", function(e) {


        
        node.attr("transform", function(d) {return returnToPosition(d, e);});

        link.attr("x1", function(d) { return d.source.x+image_size/2; })
            .attr("y1", function(d) { return d.source.y+image_size/2; })
            .attr("x2", function(d) { return d.target.x+image_size/2; })
            .attr("y2", function(d) { return d.target.y+image_size/2; });

        svg.selectAll("path").data(groups)
            .attr("d", groupPath)
           .enter().insert("path", "g")
            .style("fill", groupFill)
            .style("stroke", groupFill)
            .style("stroke-width", 40)
            .style("stroke-linejoin", "round")
            .style("opacity", .2)
            .attr("d", groupPath);

        svg.selectAll("bgp_path").data(bgp_groups)
           .enter().insert("path", "g")
            .style("fill", groupFill)
            .style("stroke", groupFill)
            .style("stroke-width", 40)
            .style("stroke-linejoin", "round")
            .style("opacity", .5)
            .attr("d", bgp_groupPath);
    
 
      });





      function showFlows(paths) {
        
        function laypath(info) {
            var arr = []
            var val = 0;
            for ( var i = 0; i < info.length ; i++) {
                arr.push({ 'x' : nodes[info[i]].x+image_size/2, 'y' : nodes[info[i]].y +image_size/2});
            }
            return arr;
        }

        function translateAlong(path) {
            var l = path.getTotalLength();
                return function(d, i, a) {
                    return function(t) {
                        var p = path.getPointAtLength(t * l);
                            return "translate(" + p.x + "," + p.y + ")";
                    };
                };
        }
        
        for (var i = 0 ; i < paths.length ; i++) {
          p = paths[i]
          var flowpath = d3.svg.line()
                        .x(function(d){return d.x;})
                        .y(function(d){return d.y;})
                        .interpolate("linear");

          var path = svg.append("svg:path")
            .attr("d", flowpath(laypath(p)))
            .style("stroke-width", 0)
            .style("fill", "none");    


          var packet = null;
          for (var j = 0 ; j < 13 ; j++) {
            packet = svg.append("rect")
                .attr("height", 5)
                .attr("width", 5)
                //.style("opacity",0.8)
                .style("fill", packetFill(i))
                .transition().duration(5000).delay((i*750)+(j*75)).ease("linear")
                .attrTween("transform", translateAlong(path.node()))
                .each("end", function() { 
                            d3.select(this).remove();
                });
          }  
            

        }
    

      }


     setInterval(function() {
        $.ajax({
            url: data_source + '/flows',
            success: function(data) {
               showFlows(data)
           },
            dataType: "json"
        });
     }, 1000); 


    var packetFill = function(i) { return pfill(i % 20); };   
     
      function returnToPosition(d, e){
        var x=0, y=0;
        var damper = 1;
        var alpha = e.alpha;
        var router_name = d.name;
        x = fixPoint(d.x, w * layout[router_name][0], alpha, damper);
        y = fixPoint(d.y, h * layout[router_name][1], alpha, damper);
        d.x = x;
        d.y = y;
        return "translate(" + x + "," + y + ")";    
      }
      
      function fixPoint(current, target, alpha, damper){
        target = target - image_size / 2;
        if (target-current < 1 && target-current > -1){
            return target;
        }
        return current + (target - current) * damper * alpha;
      }
    
      function normalize(x, lower_limit, upper_limit) {
        if (x < lower_limit) return lower_limit;
        if (x > upper_limit) return upper_limit;
        return x;
      }

    }

}


function drawTree(json, togg) {
  root = json;
  root.x0 = th / 2;
  root.y0 = 0;

  function toggleAll(d) {
    if (d.children) {
      d.children.forEach(toggleAll);
      toggle(d);
    }
  }

  // Initialize the display to show a few nodes.
  if (togg) {
    root.children.forEach(toggleAll);
    toggle(root.children[0]);
  }
  update(root);
}

function update(source) {
  var duration = d3.event && d3.event.altKey ? 5000 : 500;

  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse();

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 180; });

  // Update the nodes…
  var node = vis.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter any new nodes at the parent's previous position.
  var nodeEnter = node.enter().append("svg:g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .on("click", function(d) { toggle(d); update(d); });

  nodeEnter.append("svg:circle")
      .attr("r", 1e-6)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

  nodeEnter.append("svg:text")
      .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
      .attr("dy", ".35em")
      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
      .text(function(d) { return d.name; })
      .style("fill-opacity", 1e-6);

  // Transition nodes to their new position.
  var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

  nodeUpdate.select("circle")
      .attr("r", 4.5)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

  nodeUpdate.select("text")
      .style("fill-opacity", 1);

  // Transition exiting nodes to the parent's new position.
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .remove();

  nodeExit.select("circle")
      .attr("r", 1e-6);

  nodeExit.select("text")
      .style("fill-opacity", 1e-6);

  // Update the links…
  var link = vis.selectAll("path.link")
      .data(tree.links(nodes), function(d) { return d.target.id; });

  // Enter any new links at the parent's previous position.
  link.enter().insert("svg:path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
    .transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition links to their new position.
  link.transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition exiting nodes to the parent's new position.
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();

  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

// Toggle children.
function toggle(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
}
