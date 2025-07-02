const mainImage = document.getElementById("mainImage");
    if (!sessionStorage.getItem("mainImageAnimated")) {
      mainImage.classList.add("animate-image");
      sessionStorage.setItem("mainImageAnimated", "true");
    }

    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("menuToggle");

    let inactivityTimer;

    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("active");
      resetSidebarInactivityTimer();
    });

    function navigate(path) {
      window.location.href = `http://${window.location.host}${path}`;
    }

    function closeSidebar() {
      sidebar.classList.remove("active");
    }

    function resetSidebarInactivityTimer() {
      clearTimeout(inactivityTimer);
      inactivityTimer = setTimeout(closeSidebar, 30000);
    }

    document.addEventListener("click", function (event) {
      const isClickInside = sidebar.contains(event.target) || toggle.contains(event.target);
      if (!isClickInside && sidebar.classList.contains("active")) {
        closeSidebar();
      } else if (sidebar.classList.contains("active")) {
        resetSidebarInactivityTimer();
      }
    });