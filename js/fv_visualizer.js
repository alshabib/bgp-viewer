$(function(){
$('#filter').submit(function () {
    var inputs = $('#filter :input');
    var values = {};
    inputs.each(function() {
        values[this.name] = $(this).val();
    });
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

function getRoutes(data_source) {
     var ret = "";
     $.ajax({
           url: data_source + '/bgp1',
           dataType: 'json',
           async: false,
           success:  function (data) {
               ret = getHTML(data);
          
           }
        });
     return ret.html();
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
                return name;
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
                        drawTree(data, true)
                        //d3.select(tag).text(JSON.stringify(data, null, "  "));
                    }
    });
}
    
    

function setRegularLayout(){
  var layout = {};
  layout['SDNBGP1'] = [4/10, 1/10];
  layout['SDNBGP2'] = [9/10, 1/5]; 
  layout['FloodLight-1'] = [4/10, 1/10];
  layout['FloodLight-2'] = [7/10, 1/10];
  layout['00:00:00:00:00:00:00:a1'] = [1/4, 5/10];
  layout['00:00:00:00:00:00:00:a2'] = [3/32, 7/10];
  layout['00:00:00:00:00:00:00:a3'] = [2/3, .46];
  layout['00:00:00:00:00:00:00:a4'] = [.5, .9];
  layout['00:00:00:00:00:00:00:a5'] = [.88, .6];
  layout['00:00:00:00:00:00:00:a6'] = [.7, .8]; 
  layout['AS2'] = [.78, 0.3];
  layout['AS3'] = [0.05, 0.94];
  layout['AS4'] = [.88, 0.94];
  layout['host'] = [1/8, 5/10];  

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

function setSwitchNames() {
    var names = {}   
    names['00:00:00:00:00:00:00:a1'] = 'SLC';
    names['00:00:00:00:00:00:00:a2'] = 'LAX';
    names['00:00:00:00:00:00:00:a3'] = 'CHI';
    names['00:00:00:00:00:00:00:a4'] = 'IAH';
    names['00:00:00:00:00:00:00:a5'] = 'NYC';
    names['00:00:00:00:00:00:00:a6'] = 'ATL';
    names['AS2'] = 'AS2';
    names['AS3'] = 'AS3';
    names['AS4'] = 'AS4';
    names['host'] = "Guru's Machine";
    return names;
}
var names = setSwitchNames();

function setConnections() {
    var cons = new Array()
    cons[0] = {'id' : 2, 'name' : 'LAX-AS3'};
    cons[1] = {'id' : 4, 'name' : 'LAX-SLC'};
    cons[2] = {'id' : 3, 'name' : 'LAX-IAH'};
    cons[3] = {'id' : 1, 'name' : 'CHI-AS2'};
    cons[4] = {'id' : 5, 'name' : 'CHI-NYC'};
    cons[5] = {'id' : 6, 'name' : 'CHI-IAH'};
    cons[6] = {'id' : 7, 'name' : 'AS2-NYC'};
    cons[7] = {'id' : 3, 'name' : 'NYC-ATL'};
    cons[8] = {'id' : 9, 'name' : 'ATL-AS4'};
    cons[9] = {'id' : 10, 'name' : 'ATL-LAX'};
    cons[10] = {'id' : 11, 'name' : 'AS3-AS4'};
    return cons;
}
var cons = setConnections(); 

var m = [10, 60, 10, 60],
    tw = 1280 - m[1] - m[3],
    th = 400 - m[0] - m[2],
    i = 0,
    root, vis;

var tree = d3.layout.tree()
    .size([th, tw]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

function flipLink(state, id) {
    var updown = "down";
    if (state) {
        updown = "up";
    }
    $.ajax({
       url: "http://sdn1vpc.onlab.us:5003/link/" + id +"/" + updown,//data_source + '/flowtable/'+dpid,
       dataType: 'json',
       async: true,
       success:  function (data) {
             return;   
       }
    });
   
}

function start_demo(data_source, tag, fl_tag) {


    var h = 1000, w = 2000;//window.innerHeight - 150, w = window.innerWidth - 100;        
    var image_size = 100;
    var fill = d3.scale.category10();
    var pfill = d3.scale.category20();
    var bgmap = { 'background-repeat' : 'no-repeat', 'background-attachment': 'fixed', 'background-position':'65% 27%', 'background-image' : 'url(images/usa.png)', 'background-size' : '88% 100%' }; 


    d3.select('#controllerList').selectAll('p')
    .data(cons)
    .enter()
    .append('p')
    .append('label').attr("class", "header")
    .text(function(d) { return d.name; })
    .append("input")
    .attr("checked", true)
    .attr("type", "checkbox")
    .attr("size", "10px")
    .attr("id", function(d,i) { return d.id; })
    .on("click", function(d) {
            flipLink(!this.checked, d.id);
    });

    $(tag).css(bgmap);  

    setTimeout("setTipsy(\'"+fl_tag+"\',\'"+data_source+"\')", 3000);
//    vis = d3.select(fl_tag).append("svg:svg")
//    .attr("width", tw + m[1] + m[3])
//    .attr("height", th + m[0] + m[2])
//  .append("svg:g")
//    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

  //  var timer;

    /*var bgproute = d3.select('#bgproutes')
        .append('a').attr("xlink:href", "#").attr("id", "routes").attr("title", "None")
        .text('ONOS1');*/

    //setTipsy('#routes', data_source);
    //$('#routes').tipsy({trigger:'manual',gravity:'w', html:true, title: getRoutes(data_source)});
    /*
    $('#routes').tipsy({gravity:$.fn.tipsy.autoNS, html:true, fade:true, title: function() {
        return getRoutes(data_source);    
    }  }); 
    
    $('#routes').bind('mouseover',function(e){
       $(this).tipsy('show');
       //timer = setTimeout("$('#routes').tipsy('hide');",3000);
    });

        
    $('.tipsy').live('mouseover',function(e){
        clearTimeout(timer);
    });
    $('.tipsy').live('mouseout',function(e){
        $('#routes').tipsy('hide');
        clearTimeout(timer);
    });*/


    var svg = d3.select(tag).append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    d3.json(data_source + '/topology', draw);
    
    function draw(json) {

      //var bgp_nodes = [ { "name" : "SDNBGP1", "group" : "0" }, { "name" : "SDNBGP2", "group" : "1" }, { "name" : "FloodLight-1", "group" : "0" }, { "name" : "FloodLight-2", "group" : "1" } ];

      var bgp_nodes = [{ "name" : "SDNBGP1", "group" : "0" } ]//, { "name" : "FloodLight-1", "group" : "0" } ]

      //var nodes = json.nodes.map(Object);
      //var links = json.links.map(Object);
    
      //var groups = d3.nest().key(function(d) { return d.group; }).entries(nodes);
      
      var bgp_groups = d3.nest().key(function(d) { return d.group; }).entries(bgp_nodes);  
      
      var groupPath = function(d) {
        return "M" + 
        d3.geom.hull(d.values.map(function(i) {
                if (i.name.indexOf("a1") != -1) {
                    return [i.x , i.y  ];
                }
                if (i.name.indexOf("a2") != -1) {
                    return [i.x +image_size/2, i.y+image_size/2];
                }
                if (i.name.indexOf("a3") != -1) {
                    return [i.x+image_size/2, i.y +image_size];
                }
                if (i.name.indexOf("a4") != -1) {
                    return [i.x+image_size/2, i.y+image_size  ];
                }
                if (i.name.indexOf("a5") != -1) {
                    return [i.x + image_size, i.y+image_size/2  ];
                }
                if (i.name.indexOf("a6") != -1) {
                    return [i.x+image_size/2, i.y+image_size/2  ];
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
                .size([w, h]);
                //.nodes(json.nodes)
                //.links(json.links).start()

        var nodes = force.nodes();
        var links = force.links();

      json.nodes.forEach(function(item) {
            nodes.push(item);
        });

        json.links.forEach(function(item) {
            links.push(item);
        });

        var groups = d3.nest().key(function(d) { return d.group; }).entries(nodes);


        force.start();
    
     /* var link = svg.selectAll("line")
          .data(links)
         .enter().append("svg:line")
          .attr("stroke","green")
          .attr("stroke-width",2)
          .attr("id", function(d){return d.id;});*/

    svg.append('text').text('SDN AS - AS1')
                        .attr('x', 0.5*w)
                        .attr('y', 0.6*h)
                        //.attr('color', '#000000');
                        .attr('class', 'citylabel');

     svg.append('text').text('SLC')
                        .attr('x', 0.25*w)
                        .attr('y', 0.46*h)
                        .attr('class', 'citylabel')
    
      svg.append('text').text('LAX')
                        .attr('x', 0.1*w)
                        .attr('y', 0.66*h)
                        .attr('class', 'citylabel')

      svg.append('text').text('CHI')
                        .attr('x', 0.66*w)
                        .attr('y', 0.4*h)
                        .attr('class', 'citylabel')


      svg.append('text').text('IAH')
                        .attr('x', 0.5*w)
                        .attr('y', 0.86*h)
                        .attr('class', 'citylabel')

    
   svg.append('text').text('NYC')
                        .attr('x', 0.88*w)
                        .attr('y', 0.54*h)
                        .attr('class', 'citylabel')


    svg.append('text').text('ATL')
                        .attr('x', 0.7*w)
                        .attr('y', 0.74*h)
                        .attr('class', 'citylabel')


   svg.append('text').text('AS2')
                        .attr('x', 0.78*w)
                        .attr('y', 0.26*h)
                        .attr('class', 'citylabel')

   svg.append('text').text('AS3')
                        .attr('x', 0.1*w)
                        .attr('y', 0.84*h)
                        .attr('class', 'citylabel')

   svg.append('text').text('AS4')
                        .attr('x', 0.85*w)
                        .attr('y', 0.84*h)
                        .attr('class', 'citylabel')


    function im_size(d) {
        if (d.name.indexOf("AS") != -1) { 
            return 1.5*image_size + "px"
        } else {
            return image_size + "px";
        }
    }
        



      update_topo();
      var node = svg.selectAll("g.node")
          .data(nodes)
        .enter().append("svg:g")
          .attr("class", "node")
         .append("svg:image")
          .attr("xlink:href", function(d) {
                if (d.name.indexOf("AS") != -1) { 
                    return "images/AS-ICON.png"; 
                } else if (d.name.indexOf("00:00") != -1) { 
                    return  "images/switch.png"; 
                } else {
                    return "images/host.png";
                }
             } )
          .attr("width", function(d) {return im_size(d);} )
          .attr("height", function (d) {return im_size(d); } )
          .attr("id", function(d){ return names[d.name]; })
          //.on("click", function(d) { getFlows(data_source, fl_tag, d.name); })
        .call(force.drag);

      var bgp_node = svg.selectAll("node")
          .data(bgp_nodes)
        .enter().append("svg:g")
          .attr("class", "node")
          .append("svg:image") 
          .attr("xlink:href", function(d) {if (d.name.indexOf("FloodLight") != -1) { return "images/floodlight.png"; } else { return  "images/ONOS.png";  }} )
          .attr("width", function (d) { if (d.name.indexOf("FloodLight") != -1) { return 2*image_size + "px"; } else { return  3*image_size + "px";  }})
          .attr("height", 3*image_size + "px")
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

        svg.selectAll("line").attr("x1", function(d) { return d.source.x+image_size/2; })
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
          for (var j = 0 ; j < 7 ; j++) {
            packet = svg.append("rect")
                .attr("height", 10)
                .attr("width", 10)
                .attr("x", -10)
                .attr("y", -10)
                .style("opacity",0.8)
                .style("fill", 'orangered')
                .transition().duration(5000).delay((i*250)+(j*150)).ease("linear")
                .attrTween("transform", translateAlong(path.node()))
                .each("end", function() { 
                            d3.select(this).remove();
                });
          }  
            

        }
    

      }

     Array.prototype.diff2 = function(arr) {
        return this.filter(function(i) {
        for (var j = 0; j < arr.length ; j++) {
           if (arr[j].source === i.source.index && 
                  arr[j].target === i.target.index)
            return false;

        }
        return true;
    });
    };




     Array.prototype.diff = function(arr) {
        return this.filter(function(i) {
        for (var j = 0; j < arr.length ; j++) {
           if (arr[j].source.index === i.source && 
                  arr[j].target.index === i.target)
            return false;

        }
        return true;
    });
    };


    function cdiff(topo) {

        var changed = false;
        
        var l_adds = topo.links.diff(links);
        var l_rems = links.diff2(topo.links);


        for (var i = 0; i < l_rems.length ; i++) {
            for (var j = 0; j < links.length; j++) {
                if (links[j].source.index == l_rems[i].source.index &&
                               links[j].target.index == l_rems[i].target.index) {
                    links.splice(j,1);
                    changed = true;
                    break;
                }
            }
        }

        for (var i = 0; i < l_adds.length; i++) {
            links.push(l_adds[i]);
            changed = true;
        }

        if (changed)
             update_topo();

    } 

    function update_topo() {
       
         var l = svg.selectAll("line")
          .data(links);

        l.enter().insert("svg:line")
          .attr("stroke","green")
          .attr("stroke-width",2)
          .attr("id", function(d){return d.id;});

        l.exit().remove()
        force.start()
    }

     setInterval(function() {
        $.ajax({
            url : data_source + '/topology',
            success: function(data) {
                cdiff(data);
            },
            dataType: 'json'
        });
    }, 2000);

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
        var damper = 10;
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
  root['name'] = names[root['name']];
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
