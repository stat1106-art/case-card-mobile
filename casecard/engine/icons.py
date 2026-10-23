"""自繪線條圖示（viewBox 0 0 24 24，stroke=currentColor）。不使用外部圖示字型。"""
P = {
 "court":   '<path d="M3 9.5 12 4l9 5.5"/><path d="M4 20h16"/><path d="M6 10.5v7M10 10.5v7M14 10.5v7M18 10.5v7"/>',
 "doc":     '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 12h6M9 16h6"/>',
 "cal":     '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
 "scale":   '<path d="M12 4v16M7 20h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
 "person":  '<circle cx="12" cy="8" r="4"/><path d="M4.5 20.5c1-4 4-6 7.5-6s6.5 2 7.5 6"/>',
 "building":'<rect x="5" y="3.5" width="14" height="17" rx="1.5"/><path d="M9 8h2M13 8h2M9 12h2M13 12h2M10.5 20.5v-4h3v4"/>',
 "group":   '<circle cx="9" cy="8.5" r="3.2"/><circle cx="17" cy="9.5" r="2.5"/><path d="M3 19.5c.8-3.3 3.2-5 6-5s5.2 1.7 6 5M15.5 14.6c2.6-.2 4.6 1.4 5.2 4.4"/>',
 "clip":    '<rect x="5" y="4.5" width="14" height="16.5" rx="2"/><path d="M9 3h6v3H9zM8.5 11h7M8.5 15h5"/>',
 "gavel":   '<path d="M13.5 4.5l6 6M11 7l6 6M12.3 5.8l-4 4 6 6 4-4"/><path d="M10.3 11.8 3.5 18.6l1.9 1.9 6.8-6.8"/>',
 "bulb":    '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.3 1 2.1h5c0-.8.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
 "link":    '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 "check":   '<circle cx="12" cy="12" r="9"/><path d="M7.8 12.3l2.8 2.8 5.6-5.8"/>',
 "alert":   '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.3v.2"/>',
 "clock":   '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
 "chat":    '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
 "shield":  '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z"/>',
 "coins":   '<ellipse cx="12" cy="6.5" rx="7" ry="2.8"/><path d="M5 6.5v5c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-5M5 11.5v5c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-5"/>',
 "search":  '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
 "heart":   '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/>',
 "pulse":   '<path d="M3 12h4l2-5 4 10 2-5h6"/>',
 "overtime": '<circle cx="11" cy="13" r="8"/><path d="M11 9v4l2.5 1.6"/><path d="M20.5 4.8a3.4 3.4 0 0 1-4.3 4.3 3.4 3.4 0 1 0 4.3-4.3z"/>',
 "newhire":  '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M11 13.5h2v4"/>',
 "event":    '<path d="M5 3h7l-.4 4.5a3.1 3.1 0 0 1-6.2 0z"/><path d="M8.5 10.6V18M6 18h5"/><path d="M14 9.5h7v6h-2.5L16 18v-2.5h-2z"/>',
 "course":   '<path d="M2.5 9 12 4.5 21.5 9 12 13.5z"/><path d="M6.5 11v4.5c1.5 1.6 3.4 2.4 5.5 2.4s4-.8 5.5-2.4V11"/><path d="M21.5 9v5"/>',
 "phone":    '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M9.5 8h5M9.5 11.5h3.5"/><path d="M11 18.5h2"/>',
 "bell":     '<path d="M6 16v-5a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
 "ledger":   '<rect x="4" y="5" width="16" height="14" rx="1.5"/><path d="M12 5v14M4 10h16"/>',
 "gauge":    '<path d="M3.5 16a8.5 8.5 0 1 1 17 0"/><path d="M12 16l4.5-5"/><path d="M3.5 16h2.5M18 16h2.5"/>',
 "shieldalert": '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z"/><path d="M12 8v4.5M12 15.5v.2"/>',
}
def icon(name, size=24, stroke=2.0, cls="ic"):
    return (f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{P[name]}</svg>')
