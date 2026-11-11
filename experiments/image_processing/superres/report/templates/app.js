const views = {
    comparison: document.getElementById('view-comparison'),
    storefront: document.getElementById('view-storefront'),
};

function bindButtons(control, apply) {
    const buttons = document.querySelectorAll(`[data-${control}]`);
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const selected = button.dataset[control];
            apply(selected, buttons);
            buttons.forEach(option => {
                option.setAttribute('aria-pressed', String(option === button));
            });
        });
    });
}

bindButtons('view', view => {
    Object.entries(views).forEach(([name, section]) => {
        section.hidden = name !== view;
    });
});

for (const control of ['tone', 'crop', 'columns']) {
    bindButtons(control, (value, buttons) => {
        const classes = Array.from(buttons, button => `${control}-${button.dataset[control]}`);
        document.body.classList.remove(...classes);
        document.body.classList.add(`${control}-${value}`);
    });
}
