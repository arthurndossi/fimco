/**
 * Created by Arthur on 8/16/2017.
 */
$(document).ready(function() {
    $('#fullpage').fullpage({
        anchors: ['#', 'inform', 'advice', 'execute', 'footer'],
        sectionsColor: ['#003366', '#002952', '#001f3d', "#001429", '#333'],
        navigation: true,
        navigationPosition: 'right',
        navigationTooltips: ['Home', 'Inform', 'Advice', 'Execute', 'footer'],
        scrollBar: true
    });
});