document.querySelectorAll('.btn-delete').forEach((button) => {
  button.addEventListener('click', (event) => {
    if (!window.confirm('¿Seguro que deseas eliminar este registro?')) event.preventDefault();
  });
});
