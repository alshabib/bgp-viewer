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
  layout = {}
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

layout = setRegularLayout();

function start_demo(data_source, tag) {

    var h = 800, w = 1200;//window.innerHeight - 150, w = window.innerWidth - 100;        
    var image_size = 100;

    var force = d3.layout.force()
    .gravity(0)
    .linkDistance(10)
    .linkStrength(0)
    .charge(0)
    .size([w, h])


    var svg = d3.select(tag).append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    d3.json(data_source, draw);
    
/*    setInterval(function() {
        $.ajax({
            url: data_source,
            success: function(data) {
               update(data)
           },
            dataType: "json"
        });
     }, 2000); */
   
    setTimeout("setTipsy(\'"+tag+"\')", 3000); 
 
    function draw(json) {
    
      var link = svg.selectAll("line")
          .data(json.links)
         .enter().append("svg:line")
          .attr("stroke","green")
          .attr("stroke-width",2)
          .attr("id", function(d){return d.id;});

      var node = svg.selectAll("g.node")
          .data(json.nodes)
        .enter().append("svg:g")
          .attr("class", "node")
          .call(force.drag);

      node.append("svg:image")
          .attr("xlink:href", function(d) {if (d.name.indexOf("AS") != -1) { return "images/cloud.png"; } else { return  "images/router.png"; } } )
          .attr("width", image_size + "px")
          .attr("height", image_size + "px")
          .attr("id", function(d){return d.name;});


      force
        .nodes(json.nodes)
        .links(json.links)
        .on("tick", tick).start();
    
      function tick(e) {
        node.attr("transform", function(d) {return returnToPosition(d, e);});

        link.attr("x1", function(d) { return d.source.x+image_size/2; })
            .attr("y1", function(d) { return d.source.y+image_size/2; })
            .attr("x2", function(d) { return d.target.x+image_size/2; })
            .attr("y2", function(d) { return d.target.y+image_size/2; });
      }
      
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
