// Улучшения для админки продуктов

document.addEventListener('DOMContentLoaded', function() {
    // Добавляем drag&drop зону в секцию дополнительных изображений
    addDragDropZone();
    
    // Улучшаем inline изображения
    enhanceImageInlines();
    
    // Добавляем кнопку массовой загрузки
    addBulkUploadButton();
});

function addDragDropZone() {
    // Ищем секцию дополнительных изображений
    const additionalImagesSection = document.querySelector('fieldset:has(.description:contains("Zusätzliche Bilder"))');
    if (!additionalImagesSection) return;
    
    // Создаем drag&drop зону
    const dragZone = document.createElement('div');
    dragZone.className = 'drag-drop-zone';
    dragZone.innerHTML = `
        <div class="drag-text">📁 Перетащите изображения сюда</div>
        <div class="drag-hint">Или выберите файлы через поля ниже</div>
        <input type="file" id="bulk-file-input" multiple accept="image/*" style="display: none;">
        <button type="button" class="bulk-upload-btn" onclick="document.getElementById('bulk-file-input').click()">
            Выбрать файлы
        </button>
    `;
    
    // Добавляем в начало секции
    const fieldset = additionalImagesSection.querySelector('fieldset');
    if (fieldset) {
        fieldset.insertBefore(dragZone, fieldset.firstChild);
    }
    
    // Drag&drop события
    dragZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dragZone.classList.add('dragover');
    });
    
    dragZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dragZone.classList.remove('dragover');
    });
    
    dragZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dragZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleBulkFiles(files);
        }
    });
    
    // Обработка выбора файлов
    document.getElementById('bulk-file-input').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleBulkFiles(e.target.files);
        }
    });
}

function handleBulkFiles(files) {
    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        alert('Выберите изображения!');
        return;
    }
    
    // Находим inline форму для изображений
    const inlineFormset = document.querySelector('.inline-group');
    if (!inlineFormset) return;
    
    // Получаем текущий максимальный порядок
    let maxOrder = 0;
    const orderInputs = inlineFormset.querySelectorAll('input[name*="order"]');
    orderInputs.forEach(input => {
        const value = parseInt(input.value) || 0;
        if (value > maxOrder) maxOrder = value;
    });
    
    // Добавляем новые поля для каждого изображения
    imageFiles.forEach((file, index) => {
        addNewImageField(file, maxOrder + index + 1);
    });
    
    alert(`Добавлено ${imageFiles.length} изображений!`);
}

function addNewImageField(file, order) {
    const inlineFormset = document.querySelector('.inline-group');
    if (!inlineFormset) return;
    
    // Находим кнопку "Добавить еще"
    const addButton = inlineFormset.querySelector('.add-row a');
    if (addButton) {
        // Кликаем по кнопке добавления
        addButton.click();
        
        // Ждем появления нового поля и заполняем его
        setTimeout(() => {
            const newRow = inlineFormset.querySelector('.inline-related:last-child');
            if (newRow) {
                // Заполняем поле изображения
                const fileInput = newRow.querySelector('input[type="file"]');
                if (fileInput) {
                    // Создаем DataTransfer для установки файла
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    fileInput.files = dt.files;
                    
                    // Триггерим событие change
                    fileInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
                
                // Заполняем порядок
                const orderInput = newRow.querySelector('input[name*="order"]');
                if (orderInput) {
                    orderInput.value = order;
                }
                
                // Заполняем alt текст
                const altInput = newRow.querySelector('input[name*="alt_text"]');
                if (altInput) {
                    altInput.value = file.name.replace(/\.[^/.]+$/, ""); // Убираем расширение
                }
            }
        }, 100);
    }
}

function enhanceImageInlines() {
    // Добавляем счетчики изображений
    const inlineGroups = document.querySelectorAll('.inline-group');
    inlineGroups.forEach(group => {
        const count = group.querySelectorAll('.inline-related').length;
        const header = group.querySelector('.inline-related h3');
        if (header) {
            const counter = document.createElement('span');
            counter.className = 'image-counter';
            counter.textContent = `${count} изображений`;
            header.appendChild(counter);
        }
    });
    
    // Улучшаем превью изображений
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const container = input.closest('.inline-related');
                    if (container) {
                        // Удаляем старое превью
                        const oldPreview = container.querySelector('.image-preview');
                        if (oldPreview) oldPreview.remove();
                        
                        // Создаем новое превью
                        const preview = document.createElement('div');
                        preview.className = 'image-preview';
                        preview.innerHTML = `
                            <img src="${e.target.result}" style="max-width: 100px; max-height: 100px; border-radius: 4px;">
                        `;
                        
                        // Вставляем после поля файла
                        input.parentNode.insertBefore(preview, input.nextSibling);
                    }
                };
                
                reader.readAsDataURL(file);
            }
        });
    });
}

function addBulkUploadButton() {
    // Добавляем кнопку массовой загрузки в заголовок
    const pageHeader = document.querySelector('.page-header');
    if (pageHeader) {
        const bulkButton = document.createElement('button');
        bulkButton.type = 'button';
        bulkButton.className = 'bulk-upload-btn';
        bulkButton.textContent = '📁 Массовая загрузка изображений';
        bulkButton.onclick = showBulkUploadModal;
        
        pageHeader.appendChild(bulkButton);
    }
}

function showBulkUploadModal() {
    // Простое модальное окно для массовой загрузки
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 20px; border-radius: 8px; max-width: 500px;">
            <h3>Массовая загрузка изображений</h3>
            <p>Используйте команду:</p>
            <code style="background: #f5f5f5; padding: 10px; display: block; margin: 10px 0;">
                python manage.py bulk_upload_images [ID_продукта] [путь_к_папке]
            </code>
            <p><strong>Пример:</strong></p>
            <code style="background: #f5f5f5; padding: 10px; display: block; margin: 10px 0;">
                python manage.py bulk_upload_images 1 "C:\\Images\\Product1"
            </code>
            <button onclick="this.closest('.modal').remove()" style="margin-top: 15px;">Закрыть</button>
        </div>
    `;
    
    modal.className = 'modal';
    document.body.appendChild(modal);
}
