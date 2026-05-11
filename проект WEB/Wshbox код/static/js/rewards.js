(function () {
  const rewards = [
    { id: 1, name: "Монетка удачи", icon: "bi-cash-coin", color: "text-warning" },
    { id: 2, name: "Золотой старт", icon: "bi-rocket-takeoff", color: "text-primary" },
    { id: 3, name: "Финишная искра", icon: "bi-stars", color: "text-warning" },
    { id: 4, name: "Сила привычки", icon: "bi-lightning-charge", color: "text-warning" },
    { id: 5, name: "Терпение мастера", icon: "bi-hourglass-split", color: "text-secondary" },
    { id: 6, name: "Маленькая победа", icon: "bi-award", color: "text-success" },
    { id: 7, name: "Большая победа", icon: "bi-award-fill", color: "text-success" },
    { id: 8, name: "Суперфокус", icon: "bi-bullseye", color: "text-danger" },
    { id: 9, name: "Режим героя", icon: "bi-shield-check", color: "text-success" },
    { id: 10, name: "Магическая искра", icon: "bi-magic", color: "text-primary" },
    { id: 11, name: "Сердце мечты", icon: "bi-heart-fill", color: "text-danger" },
    { id: 12, name: "Смелый шаг", icon: "bi-footprints", color: "text-secondary" },
    { id: 13, name: "Точка роста", icon: "bi-graph-up-arrow", color: "text-success" },
    { id: 14, name: "Новый уровень", icon: "bi-bar-chart-line-fill", color: "text-primary" },
    { id: 15, name: "Ключ к цели", icon: "bi-key-fill", color: "text-warning" },
    { id: 16, name: "Секретный сундук", icon: "bi-box2-heart-fill", color: "text-danger" },
    { id: 17, name: "Счастливый билет", icon: "bi-ticket-perforated-fill", color: "text-primary" },
    { id: 18, name: "Корона усилий", icon: "bi-crown-fill", color: "text-warning" },
    { id: 19, name: "Медаль дисциплины", icon: "bi-patch-check-fill", color: "text-success" },
    { id: 20, name: "Награда за путь", icon: "bi-signpost-2-fill", color: "text-secondary" },
    { id: 21, name: "Скорость прогресса", icon: "bi-speedometer2", color: "text-primary" },
    { id: 22, name: "Уверенный темп", icon: "bi-activity", color: "text-success" },
    { id: 23, name: "Мечта близко", icon: "bi-compass-fill", color: "text-primary" },
    { id: 24, name: "Стальная воля", icon: "bi-gem", color: "text-info" },
    { id: 25, name: "Идеальный день", icon: "bi-sunrise-fill", color: "text-warning" },

    { id: 26, name: "Книга силы", icon: "bi-book-fill", color: "text-primary" },
    { id: 27, name: "Творческий огонь", icon: "bi-palette-fill", color: "text-danger" },
    { id: 28, name: "Звезда усердия", icon: "bi-star-fill", color: "text-warning" },
    { id: 29, name: "Нить вдохновения", icon: "bi-bezier2", color: "text-secondary" },
    { id: 30, name: "Мастер плана", icon: "bi-calendar2-check-fill", color: "text-success" },
    { id: 31, name: "Чистый лист", icon: "bi-file-earmark", color: "text-secondary" },
    { id: 32, name: "Энергия действия", icon: "bi-battery-charging", color: "text-success" },
    { id: 33, name: "Секунда гордости", icon: "bi-stopwatch-fill", color: "text-primary" },
    { id: 34, name: "Снежный ком", icon: "bi-snow", color: "text-info" },
    { id: 35, name: "Океан терпения", icon: "bi-water", color: "text-primary" },
    { id: 36, name: "Лист прогресса", icon: "bi-tree-fill", color: "text-success" },
    { id: 37, name: "Цветок результата", icon: "bi-flower1", color: "text-danger" },
    { id: 38, name: "Взлёт мотивации", icon: "bi-arrow-up-right-circle-fill", color: "text-success" },
    { id: 39, name: "Тёплый успех", icon: "bi-emoji-smile-fill", color: "text-warning" },
    { id: 40, name: "Спокойная уверенность", icon: "bi-peace-fill", color: "text-success" },
    { id: 41, name: "Смелая идея", icon: "bi-lightbulb-fill", color: "text-warning" },
    { id: 42, name: "Чемпион дня", icon: "bi-trophy-fill", color: "text-warning" },
    { id: 43, name: "Комета цели", icon: "bi-moon-stars-fill", color: "text-primary" },
    { id: 44, name: "Маяк пути", icon: "bi-lighthouse", color: "text-info" },
    { id: 45, name: "Курс на мечту", icon: "bi-send-fill", color: "text-primary" },
    { id: 46, name: "Подарок себе", icon: "bi-gift-fill", color: "text-danger" },
    { id: 47, name: "Печать успеха", icon: "bi-seal-fill", color: "text-success" },
    { id: 48, name: "Момент вау", icon: "bi-emoji-sunglasses-fill", color: "text-warning" },
    { id: 49, name: "Планета прогресса", icon: "bi-globe2", color: "text-primary" },
    { id: 50, name: "Легенда", icon: "bi-fire", color: "text-danger" },
  ];

  window.WISHBOX_REWARDS = rewards;

  window.WishboxRewards = {
    getById(id) {
      const n = Number(id);
      return rewards.find((r) => r.id === n) || null;
    },
    getUnlocked() {
      try {
        const raw = localStorage.getItem("wishbox-unlocked-rewards");
        const arr = raw ? JSON.parse(raw) : [];
        return Array.isArray(arr) ? arr : [];
      } catch (e) {
        return [];
      }
    },
    unlock(id, meta) {
      const reward = this.getById(id);
      if (!reward) return null;
      const unlocked = this.getUnlocked();
      const exists = unlocked.some((x) => Number(x.id) === Number(id));
      if (!exists) {
        unlocked.unshift({
          id: reward.id,
          unlockedAt: new Date().toISOString(),
          wishTitle: meta && meta.wishTitle ? String(meta.wishTitle) : null,
        });
        localStorage.setItem("wishbox-unlocked-rewards", JSON.stringify(unlocked.slice(0, 200)));
      }
      return reward;
    },
  };
})();

