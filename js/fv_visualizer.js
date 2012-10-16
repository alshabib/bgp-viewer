function setTipsy(tag) {
    $(tag + ' svg image').tipsy({ 
          //trigger: 'manual',
          gravity: $.fn.tipsy.autoNS,
          html: true, 
          fade: true,
          title: function(){
            return $(this).attr('id');
          }   
    });   
}

function reset() {

    $(".spinner").hide();

}

function setRegularLayout(){
  var layout = {};
  layout['00:00:00:00:00:00:00:a1'] = [1/10, 1/4];
  layout['00:00:00:00:00:00:00:a2'] = [1/10, 3/4];
  layout['00:00:00:00:00:00:00:a3'] = [2/10, 2/4];
  layout['00:00:00:00:00:00:00:a4'] = [3/10, 1/4];
  layout['00:00:00:00:00:00:00:a5'] = [3/10, 3/4];
  
  layout['AS1'] = [5/10, 1/4];
  layout['AS2'] = [4/10, 3/4];
  layout['AS3'] = [6/10, 3/4];

  layout['00:00:00:00:00:00:00:b1'] = [7/10, 1/4];
  layout['00:00:00:00:00:00:00:b2'] = [7/10, 3/4];
  layout['00:00:00:00:00:00:00:b3'] = [8/10, 2/4];
  layout['00:00:00:00:00:00:00:b4'] = [9/10, 1/4];
  layout['00:00:00:00:00:00:00:b5'] = [9/10, 3/4];
  return layout;
}

var layout = setRegularLayout();

function start_demo(data_source, flow_source, tag) {

    var h = 800, w = 1200;//window.innerHeight - 150, w = window.innerWidth - 100;        
    var image_size = 100;
    var fill = d3.scale.category10();
    var pfill = d3.scale.category20b();

    var svg = d3.select(tag).append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    d3.json(data_source, draw);
    
    setTimeout("setTipsy(\'"+tag+"\')", 3000); 
 
    function draw(json) {

      var nodes = json.nodes.map(Object);
    
      var groups = d3.nest().key(function(d) { return d.group; }).entries(nodes);

      var groupPath = function(d) {
        return "M" + 
        d3.geom.hull(d.values.map(function(i) { 
                if (i.name.indexOf("a1") != -1) {
                    return [i.x, i.y ];
                }
                if (i.name.indexOf("a2") != -1) {
                    return [i.x, i.y + image_size];
                }
                if (i.name.indexOf("b4") != -1) {
                    return [i.x + image_size, i.y ];
                }
                 if (i.name.indexOf("b5") != -1) {
                    return [i.x + image_size, i.y + image_size ];
                }
                return [i.x + image_size/2, i.y + image_size / 2]; }))
            .join("L")
        + "Z";
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
          .attr("id", function(d){return d.name;})
        .call(force.drag);


    


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
    
 
 
      });



     function transitionPacket(path) {
     }



      function showFlows(paths) {
        
        function laypath(info) {
            var arr = []
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
            path = paths[i]
            var flowpath = d3.svg.line()
                        .x(function(d){return d.x;})
                        .y(function(d){return d.y;})
                        .interpolate("linear");

          var path = svg.append("svg:path")
            .attr("d", flowpath(laypath(path)))
            .style("stroke-width", 0)
            .style("fill", "none");    


            var packet = svg.append("circle")
                .attr("r", 10)
                .style("opacity",0.8)
                .style("fill", packetFill(i))
                .transition().duration(4000)
                .attrTween("transform", translateAlong(path.node()))
                .each("end", function() { 
                            d3.select(this).remove();
                });

            

        }
    

      }


     setInterval(function() {
        $.ajax({
            url: flow_source,
            success: function(data) {
               showFlows(data)
           },
            dataType: "json"
        });
     }, 2000); 


    var packetFill = function(i) { return fill(i & 5); };   
     
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
