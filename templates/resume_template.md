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
            line-height: 1.4;
            color: #000000;
            margin: 0;
            padding: 0;
            font-size: 15px;
        }
        .header {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #000000;
            padding-bottom: 15px;
        }
        .logo {
            max-width: 120px;
            height: auto;
            margin-bottom: 15px;
        }
        .header-content {
            text-align: center;
        }

        .content {
            margin: 0;
        }
        h1, h2, h3 {
            color: #000000;
            font-size: 15px;
        }
        h1 {
            font-size: 15px;
            text-align: right;
            margin-bottom: 2px;
            padding-bottom: 2px;
        }
        h2 {
            font-size: 15px;
            text-align: right;
            margin-top: 2px;
            margin-bottom: 15px;
            border-bottom: 1px solid #000000;
            padding-bottom: 2px;
        }
        /* Section headers should be underlined */
        h3 {
            font-size: 15px;
            margin-top: 20px;
            margin-bottom: 10px;
            text-decoration: underline;
        }
        ul {
            margin: 5px 0;
            padding-left: 20px;
            list-style-type: disc;
        }
        li {
            margin-bottom: 2px;
            font-size: 15px;
            list-style-type: disc;
            list-style-position: outside;
        }
        p {
            font-size: 15px;
        }
        .section {
            margin-bottom: 25px;
        }
        strong {
            color: #333333;
        }
        .company {
            font-style: italic;
            color: #666666;
        }
        .date {
            float: right;
            color: #666666;
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