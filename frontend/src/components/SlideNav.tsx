interface Section {
  key: string;
  title: string;
  icon: string;
}

interface SlideNavProps {
  sections: readonly Section[];
  activeIndex: number;
  onNavigate: (index: number) => void;
}

export function SlideNav({ sections, activeIndex, onNavigate }: SlideNavProps) {
  return (
    <nav className="slide-nav">
      {sections.map((section, index) => (
        <button
          key={section.key}
          className={`slide-nav-item ${index === activeIndex ? 'active' : ''}`}
          onClick={() => onNavigate(index)}
          title={section.title}
        >
          <span className="slide-nav-icon">{section.icon}</span>
          <span className="slide-nav-label">{section.title}</span>
        </button>
      ))}
    </nav>
  );
}
