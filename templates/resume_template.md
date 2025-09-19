<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Professional Resume</title>
    <style>
        @page {
            margin: 1in;
            size: A4;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            /* border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px; */
        }
        .logo {
            max-width: 150px;
            height: auto;
            margin-right: 20px;
            flex-shrink: 0;
        }
        .header-content {
            flex: 1;
        }
        .content {
            margin: 0;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        h2 {
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 8px;
        }
        h3 {
            font-size: 16px;
            margin-bottom: 8px;
        }
        ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        li {
            margin-bottom: 2px;
        }
        .section {
            margin-bottom: 25px;
        }
        strong {
            color: #2c3e50;
        }
        .company {
            font-style: italic;
            color: #7f8c8d;
        }
        .date {
            float: right;
            color: #95a5a6;
            font-size: 14px;
        }
        .clearfix::after {
            content: "";
            display: table;
            clear: both;
        }
    </style>
</head>
<body>
    <div class="header">
        {% if include_logo and logo_path %}
        <img src="file:///{{ logo_path }}" alt="Brainium Logo" class="logo">
        {% endif %}
    </div>
    <div class="content">
        {{ cv_content }}
    </div>
</body>
</html>