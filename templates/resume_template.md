<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Professional Resume</title>
    <style>
        @page {
            margin: 1in;
            size: A4;
            @frame header_frame {
                -pdf-frame-content: header;
                left: 50pt;
                top: 20pt;
                height: 30pt;
                width: 500pt;
            }
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .logo {
            max-width: 120px;
            height: auto;
            margin-right: 15px;
            flex-shrink: 0;
        }
        .header-content {
            flex: 1;
        }
        /* Header frame for every page */
        .page-header {
            -pdf-frame-content: header;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 30pt;
            padding: 10pt;
            background: white;
            border-bottom: 1px solid #e0e0e0;
        }
        .page-header .small-logo {
            max-width: 80px;
            height: auto;
        }
        .content {
            margin: 0;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        h1 {
            font-size: 28px;
            margin-bottom: 5px;  /* Reduced spacing after name */
        }
        h2 {
            font-size: 16px;  /* Made role smaller */
            margin-top: 0px;   /* Reduced spacing before role */
            margin-bottom: 15px;
            font-weight: 500;  /* Slightly lighter weight for role */
        }
        /* First h2 after h1 should be treated as role */
        h1 + h2 {
            font-size: 14px;  /* Even smaller for role */
            color: #666;      /* Lighter color for role */
            margin-top: 2px;  /* Minimal space between name and role */
            margin-bottom: 20px;
        }
        /* Regular h2 sections */
        h2:not(h1 + h2) {
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
    <!-- Header for every page -->
    {% if include_logo and logo_path %}
    <div class="page-header" id="header">
        <img src="file:///{{ logo_path }}" alt="Brainium Logo" class="small-logo">
    </div>
    {% endif %}
    
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