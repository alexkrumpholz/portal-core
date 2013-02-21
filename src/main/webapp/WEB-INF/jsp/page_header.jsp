<%@ taglib prefix='security' uri='http://www.springframework.org/security/tags' %>
   <div id="header-container">
      <div id="logo">
         <h1>
            <a href="#" onclick="window.open('about.html','AboutWin','toolbar=no, menubar=no,location=no,resizable=no,scrollbars=yes,statusbar=no,top=100,left=200,height=650,width=450');return false"><img alt="VGL Header" src="img/img-auscope-banner.gif"></a>
         </h1>
      </div>
      <div id="menu">
         <ul >
            <security:authorize ifAllGranted="ROLE_ADMINISTRATOR">
                <li ><a href="admin.html">Administration<span></span></a></li>
            </security:authorize>

            <li><a id="help-button">Help<span></span></a></li>
            <li <%if (request.getRequestURL().toString().contains("/gmap.jsp")) {%>class="current" <%} %>><a href="gmap.html">VGL Portal<span></span></a></li>
            <li <%if (request.getRequestURL().toString().contains("/jobbuilder.jsp")) {%>class="current" <%} %>><a href="jobbuilder.html">Submit Jobs<span></span></a></li>
            <li <%if (request.getRequestURL().toString().contains("/joblist.jsp")) {%>class="current" <%} %>><a href="joblist.html">Monitor Jobs<span></span></a></li>

            <security:authorize ifAllGranted="ROLE_ANONYMOUS">
                <li><a href="login.html">Login<span></span></a></li>
            </security:authorize>

            <security:authorize ifNotGranted="ROLE_ANONYMOUS">
                <li ><a href="j_spring_security_logout">Logout<span></span></a></li>
            </security:authorize>
         </ul>
      </div>
      <span id="latlng" class="input-text"></span>
   </div>
