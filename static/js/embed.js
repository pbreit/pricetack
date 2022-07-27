if (window.pricetack == undefined)
   window.pricetack = {};

window.pricetack.embed = function(host) {
    document.write('<iframe id="pricetack" name="pricetack" src="http://pb-dev.pricetack.com:8001/embed/listings?count=4" scrolling="no" frameborder="0" border="0" width="100%" height="1000" style="width: 100%; height: 1000px; border: 0; display: block;"></iframe>');
    return this;
};
try {
    window.pricetack.embed();
} catch(e) {
    document.write("<div style=\"padding: 10px; font-size: 12px; font-family: 'sans-serif'; background: #fff; color:#000;\">Error loading Pricetack: " + e + "</div>");
}