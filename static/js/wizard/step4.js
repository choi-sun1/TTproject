document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('detailsForm');
    const submitBtn = document.getElementById('submitBtn');
    const checklistContainer = document.getElementById('checklistContainer');

    // 기본 체크리스트 아이템 추가
    const defaultItems = [
        '여권/신분증',
        '숙소 예약 확인',
        '필수 약품'
    ];
    
    defaultItems.forEach(item => addChecklistItem(item));
    
    // 예산 입력 시 총액 계산
    document.querySelectorAll('.budget-input input').forEach(input => {
        input.addEventListener('input', calculateTotalBudget);
    });
    
    // 폼 제출 처리
    if (submitBtn) {
        submitBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            try {
                // 예산 데이터 수집
                const budgets = {};
                document.querySelectorAll('.budget-input input').forEach(input => {
                    const amount = parseInt(input.value) || 0;
                    if (amount > 0) {
                        budgets[input.name.replace('_budget', '')] = amount;
                    }
                });

                // 체크리스트 데이터 수집
                const checklist = Array.from(document.querySelectorAll('.checklist-item input[type="text"]'))
                    .map(input => input.value.trim())
                    .filter(text => text);

                // 전송할 데이터 구성
                const formData = {
                    budgets: budgets,
                    checklist: checklist,
                    is_public: form.querySelector('[name="is_public"]').checked,
                    notes: form.querySelector('[name="notes"]').value
                };

                // 서버로 데이터 전송
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    throw new Error(data.error || '저장에 실패했습니다.');
                }
            } catch (error) {
                console.error('Save error:', error);
                alert(error.message);
            }
        });
    }
});

// 체크리스트 아이템 추가 함수
function addChecklistItem(value = '') {
    const container = document.getElementById('checklistContainer');
    const item = document.createElement('div');
    item.className = 'checklist-item';
    item.innerHTML = `
        <i class="fas fa-grip-vertical"></i>
        <input type="text" placeholder="체크리스트 항목 입력" value="${value}">
        <button type="button" class="remove-btn" onclick="this.closest('.checklist-item').remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(item);
}

// 총 예산 계산 함수
function calculateTotalBudget() {
    let total = 0;
    document.querySelectorAll('.budget-input input').forEach(input => {
        total += parseInt(input.value) || 0;
    });
    document.getElementById('totalBudget').textContent = total.toLocaleString();
}
