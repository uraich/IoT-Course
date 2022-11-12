{% args sensor %}
<html>
<head>
  <title>SHT30 temperature and humidity</title>
  <style>
  table, th, td {
  	 border: 1px solid black;
  	 padding: 5px;
	 }
  table {
  	border-spacing: 15px;
  }
  </style>
</head>
<body>
<h1> SHT30 </h1>
<table>
  <tr>
    <th align="left">measurement</th>
    <th align="left">value</th>
    <th align="left">timestamp</th>
  </tr> 
  <tr>
    <td>temperature:</td>
    <td>{{sensor['tmpr']}} &degC</td>
    <td>taken at: {{sensor['timeStamp']}}</td>
  </tr>
  <tr>
    <td>humidity:</td>
    <td>{{sensor['hmdty']}} %</td>
  </tr>
</table>

</body>

</html>
