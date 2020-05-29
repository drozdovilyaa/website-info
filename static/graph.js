$(document).ready(function() {
	$(chart_id).highcharts({
		chart: chart,
		title: title,
		xAxis: xAxis,
		yAxis: yAxis,
		series: series,
	});
});

$(document).ready(function() {
	$(chart_id_2).highcharts({
		chart: chart_2,
		title: title_2,
		xAxis: xAxis_2,
		yAxis: yAxis_2,
		series: series_2,
	});
});