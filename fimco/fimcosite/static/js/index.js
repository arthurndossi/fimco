/**
 * Created by Arthur on 8/16/2017.
 */
$(document).ready(function() {
    $('#fullpage').fullpage({
        anchors: ['1', '2', '3'],
        sectionsColor: ['#003366', '#002952', '#001f3d'],
        navigation: true,
        navigationPosition: 'right',
        navigationTooltips: ['First page', 'Second page', 'Third page']
    });
});