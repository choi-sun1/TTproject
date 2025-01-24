class ScheduleBuilder {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentDay = 1;
        this.scheduleData = new Map();
        this.initializeDragAndDrop();
    }

    initializeDragAndDrop() {
        // 미할당 장소 목록 드래그 설정
        new Sortable(document.getElementById('unassignedPlacesList'), {
            group: 'places',
            animation: 150,
            onEnd: (evt) => this.handleDragEnd(evt)
        });

        // 타임라인 드래그 설정
        new Sortable(document.getElementById('scheduleTimeline'), {
            group: 'places',
            animation: 150,
            onAdd: (evt) => this.handlePlaceAdd(evt),
            onUpdate: (evt) => this.updateOrder(evt)
        });
    }

    handlePlaceAdd(evt) {
        const placeElement = evt.item;
        this.showTimeInputDialog(placeElement)
            .then(timeData => {
                if (timeData) {
                    this.updatePlaceTime(placeElement, timeData);
                    this.saveSchedule();
                }
            });
    }

    async showTimeInputDialog(placeElement) {
        return new Promise((resolve) => {
            const dialog = document.createElement('div');
            dialog.className = 'time-input-dialog';
            dialog.innerHTML = `
                <div class="dialog-content">
                    <h3>시간 설정</h3>
                    <div class="time-inputs">
                        <input type="time" id="startTime" required>
                        <span>~</span>
                        <input type="time" id="endTime" required>
                    </div>
                    <div class="dialog-actions">
                        <button type="button" class="btn-save">저장</button>
                        <button type="button" class="btn-cancel">취소</button>
                    </div>
                </div>
            `;
            document.body.appendChild(dialog);

            // 이벤트 핸들러 등록
            dialog.querySelector('.btn-save').onclick = () => {
                const startTime = dialog.querySelector('#startTime').value;
                const endTime = dialog.querySelector('#endTime').value;
                dialog.remove();
                resolve({ startTime, endTime });
            };

            dialog.querySelector('.btn-cancel').onclick = () => {
                dialog.remove();
                resolve(null);
            };
        });
    }

    updatePlaceTime(placeElement, timeData) {
        const timeDisplay = document.createElement('div');
        timeDisplay.className = 'time-display';
        timeDisplay.innerHTML = `${timeData.startTime} ~ ${timeData.endTime}`;
        placeElement.insertBefore(timeDisplay, placeElement.firstChild);
        
        placeElement.dataset.startTime = timeData.startTime;
        placeElement.dataset.endTime = timeData.endTime;
    }

    updateOrder() {
        const places = Array.from(document.querySelectorAll('#scheduleTimeline .place-item'));
        places.forEach((place, index) => {
            place.dataset.order = index + 1;
        });
        this.saveSchedule();
    }

    saveSchedule() {
        const daySchedule = Array.from(document.querySelectorAll('#scheduleTimeline .place-item'))
            .map(place => ({
                id: place.dataset.placeId,
                order: parseInt(place.dataset.order),
                startTime: place.dataset.startTime,
                endTime: place.dataset.endTime
            }));

        this.scheduleData.set(this.currentDay, daySchedule);
        this.notifyChange();
    }

    notifyChange() {
        const event = new CustomEvent('scheduleChange', {
            detail: {
                day: this.currentDay,
                schedule: this.scheduleData.get(this.currentDay)
            }
        });
        this.container.dispatchEvent(event);
    }

    switchDay(dayNumber) {
        this.currentDay = dayNumber;
        this.loadDaySchedule(dayNumber);
    }

    loadDaySchedule(dayNumber) {
        const schedule = this.scheduleData.get(dayNumber) || [];
        const timeline = document.getElementById('scheduleTimeline');
        timeline.innerHTML = schedule.map(place => this.createPlaceElement(place)).join('');
    }

    createPlaceElement(place) {
        return `
            <div class="place-item" 
                 data-place-id="${place.id}"
                 data-order="${place.order}"
                 data-start-time="${place.startTime}"
                 data-end-time="${place.endTime}">
                <div class="time-display">${place.startTime} ~ ${place.endTime}</div>
                <h4>${place.name}</h4>
                <p>${place.address}</p>
                <button type="button" class="btn-remove" onclick="scheduleBuilder.removePlace(${place.id})">×</button>
            </div>
        `;
    }

    getAllScheduleData() {
        return Array.from(this.scheduleData.entries())
            .map(([day, schedule]) => ({
                day_number: day,
                places: schedule
            }));
    }
}
