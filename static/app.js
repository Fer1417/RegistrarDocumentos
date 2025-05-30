document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const searchInput = document.getElementById("searchInput");
  const tableBody = document.querySelector("#usersTable tbody");
  let allUsers = [];

  async function loadUsers() {
    const res = await fetch("/api/users");
    allUsers = await res.json();
    renderTable(allUsers);
    searchInput.addEventListener("input", () => {
      const filtered = allUsers.filter(u =>
        u.nombre_completo.toLowerCase().includes(searchInput.value.toLowerCase()) ||
        u.id.toString().includes(searchInput.value)
      );
      renderTable(filtered);
    });
  }

  const docTypeSelect = document.getElementById("docType");
  const cedulaOptions = document.getElementById("cedulaOptions");

  if (docTypeSelect) {
  docTypeSelect.addEventListener("change", () => {
    if (docTypeSelect.value === "cedula") {
      cedulaOptions.style.display = "block";
      document.querySelectorAll("input[name='cedula_tipo']").forEach(input => {
        input.required = true;
      });
    } else {
      cedulaOptions.style.display = "none";
      document.querySelectorAll("input[name='cedula_tipo']").forEach(input => {
        input.required = false;
      });
    }
  });
}


  function renderTable(data) {
    tableBody.innerHTML = "";
    data.forEach(u => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${u.id}</td>
        <td>${u.nombre_completo}</td>
        <td>${u.curp || "No ingresada"}</td>
        <td>${u.rfc || "No ingresada"}</td>
        <td><button class="btn btn-outline-primary btn-sm" onclick="showUserDetails(${u.id}, '${u.nombre_completo}')"><i class="fa-solid fa-eye"></i></button></td>
        <td><button class="btn btn-outline-secondary btn-sm" onclick="openUploadForm(${u.id}, '${u.nombre_completo}')"><i class="fa-solid fa-upload"></i></button></td>
      `;
      tableBody.appendChild(tr);
    });
  }

  window.showUserDetails = async function(id, nombre) {
    const res = await fetch(`/api/users/${id}`);
    const user = await res.json();

    document.getElementById("modalUserId").textContent = user.id;
    document.getElementById("modalUserName").textContent = nombre;

    const fields = document.querySelectorAll("#modalUserFields span");
    const values = [
      user.curp,
      user.rfc,
      user.imss,
      user.numero_ine,
      user.domicilio,
      user.cursos.join(", ") || "-",
      user.cedulas.join(", ") || "-",
      user.regimenes.join(", ") || "-"
    ];
    fields.forEach((el, i) => el.textContent = values[i] || "No registrado");

    const modal = new bootstrap.Modal(document.getElementById("userDetailsModal"));
    modal.show();
  };

  window.openUploadForm = function(id, nombre) {
    document.getElementById("uploadUserId").value = id;
    document.getElementById("uploadUserName").textContent = nombre;
    const modal = new bootstrap.Modal(document.getElementById("uploadModal"));
    modal.show();
  };

  const uploadForm = document.getElementById("uploadForm");
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = new FormData(uploadForm);

      if (document.getElementById("docType").value === "cedula") {
        const formatoCedula = document.querySelector("input[name='cedula_tipo']:checked");
        if (formatoCedula) {
          form.append("formato_cedula", formatoCedula.value);
        }
      }

      Swal.fire({
        title: 'Procesando...',
        html: 'Esto puede tardar unos segundos...',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        }
      });

      try {
        const res = await fetch("/upload/document", {
          method: "POST",
          body: form
        });
        const result = await res.json();

        if (result.validado) {
          Swal.fire({
            icon: "success",
            title: "Documento validado con éxito",
            html: "El documento se validó correctamente.",
            showConfirmButton: true
          }).then(() => {
            uploadForm.reset();
            location.reload();
          });

        } else {
          Swal.fire({
            icon: "error",
            title: "Error",
            html: ` <p>${result.mensaje || "Hubo un problema al validar el documento."}</p> `
          });
        }

      } catch (error) {
        Swal.fire({
          icon: "error",
          title: "Error interno",
          html: `<p>No se pudo validar el documento.</p>`
        });
      }
    });
  }

  loadUsers();
});
