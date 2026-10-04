document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('http://localhost:8000/api/v1/dashboard/stats');
        const result = await response.json();
        
        if (result.success && result.data) {
            const stats = result.data.stats;
            
            // Populate KPI Cards
            document.getElementById('kpi-users').textContent = stats.total_users || 0;
            document.getElementById('kpi-queries').textContent = stats.total_queries || 0;
            document.getElementById('kpi-pdfs').textContent = stats.total_pdfs || 0;
            document.getElementById('kpi-answers').textContent = stats.saved_answers || 0;
            document.getElementById('kpi-support').textContent = stats.support_requests || 0;
            document.getElementById('kpi-uptime').textContent = stats.system_uptime + '%' || '99.9%';
            
            // Populate Recent Activity
            const activity = result.data.recent_activity;
            
            // Users
            const usersContainer = document.getElementById('recent-users-container');
            if(usersContainer) {
                if(activity.users && activity.users.length > 0) {
                    usersContainer.innerHTML = activity.users.map(u => {
                        const initials = u.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
                        const timeStr = u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Just now';
                        return `
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="width: 32px; height: 32px; border-radius: 50%; background: #3b82f6; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; color: #fff;">${initials}</div>
                                <div>
                                    <div style="font-size: 0.8rem; font-weight: 600; color: #fff;">${u.name}</div>
                                    <div style="font-size: 0.65rem; color: #9ca3af;">${u.email}</div>
                                </div>
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                                <span class="badge badge-primary">${u.role}</span>
                                <span style="font-size: 0.65rem; color: #9ca3af;">${timeStr}</span>
                            </div>
                        </div>`;
                    }).join('');
                } else {
                    usersContainer.innerHTML = '<div style="text-align: center; color: #9ca3af; font-size: 0.8rem; padding: 20px 0;">No recent users</div>';
                }
            }

            // Queries
            const queriesContainer = document.getElementById('recent-queries-container');
            if(queriesContainer) {
                if(activity.queries && activity.queries.length > 0) {
                    queriesContainer.innerHTML = activity.queries.map(q => {
                        const timeStr = q.created_at ? new Date(q.created_at).toLocaleDateString() : 'Just now';
                        return `
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                            <div style="display: flex; align-items: flex-start; gap: 10px; overflow: hidden;">
                                <i data-lucide="message-square" style="width: 14px; height: 14px; color: #10b981; flex-shrink: 0; margin-top: 2px;"></i>
                                <span style="font-size: 0.75rem; color: #d1d5db; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${q.content}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
                                <span style="font-size: 0.65rem; color: #9ca3af; width: 45px; text-align: right;">${timeStr}</span>
                            </div>
                        </div>`;
                    }).join('');
                } else {
                    queriesContainer.innerHTML = '<div style="text-align: center; color: #9ca3af; font-size: 0.8rem; padding: 20px 0;">No recent queries</div>';
                }
            }

            // PDFs
            const pdfsContainer = document.getElementById('recent-pdfs-container');
            if(pdfsContainer) {
                if(activity.pdfs && activity.pdfs.length > 0) {
                    pdfsContainer.innerHTML = activity.pdfs.map(p => {
                        const timeStr = p.created_at ? new Date(p.created_at).toLocaleDateString() : 'Just now';
                        const sizeMB = p.file_size ? (p.file_size / (1024*1024)).toFixed(1) : 0;
                        return `
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background: rgba(239, 68, 68, 0.2); color: #ef4444; width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;"><i data-lucide="file-text" style="width:16px; height:16px;"></i></div>
                            <div style="flex: 1; overflow: hidden;">
                                <div style="font-size: 0.75rem; font-weight: 500; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${p.original_filename || p.title}</div>
                                <div style="font-size: 0.65rem; color: #9ca3af; margin-top: 2px;">${sizeMB} MB &bull; ${timeStr}</div>
                            </div>
                        </div>`;
                    }).join('');
                } else {
                    pdfsContainer.innerHTML = '<div style="text-align: center; color: #9ca3af; font-size: 0.8rem; padding: 20px 0;">No recent PDFs</div>';
                }
            }

            // Analytics Graph
            if (result.data.analytics) {
                const graphData = result.data.analytics.graph;
                const chartContainer = document.getElementById('analytics-chart-container');
                if (chartContainer) {
                    const maxCount = Math.max(...graphData.map(d => d.count), 1);
                    const barsHtml = graphData.map(d => {
                        const heightPct = (d.count / maxCount) * 100;
                        const dateObj = new Date(d.date);
                        const label = dateObj.toLocaleDateString('en-US', { day: 'numeric', month: 'short' });
                        return `
                        <div style="display: flex; flex-direction: column; justify-content: flex-end; align-items: center; flex: 1; height: 100%; group">
                            <div style="position: relative; width: 30px; height: 100%; display: flex; align-items: flex-end; justify-content: center;">
                                <div style="background: rgba(16, 185, 129, 0.2); width: 100%; height: 100%; position: absolute; bottom: 0; border-radius: 4px;"></div>
                                <div style="background: #10b981; width: 100%; height: ${heightPct}%; border-radius: 4px; position: relative; z-index: 2; transition: height 0.5s;">
                                    <div style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); background: #000; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; opacity: 1; pointer-events: none;">${d.count}</div>
                                </div>
                            </div>
                            <div style="font-size: 0.65rem; color: #9ca3af; margin-top: 8px;">${label}</div>
                        </div>`;
                    }).join('');
                    
                    chartContainer.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: flex-end; height: 100%; width: 100%; padding-top: 20px; gap: 10px;">
                        ${barsHtml}
                    </div>`;
                }

                // Analytics Categories
                const categoriesData = result.data.analytics.categories;
                const catContainer = document.getElementById('analytics-categories-container');
                if (catContainer) {
                    const colors = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4', '#eab308', '#6b7280'];
                    const icons = ['book', 'edit-3', 'user-plus', 'file-check', 'credit-card', 'library', 'home', 'more-horizontal'];
                    
                    catContainer.innerHTML = categoriesData.map((c, i) => {
                        const color = colors[i % colors.length];
                        const icon = icons[i % icons.length];
                        return `
                        <div style="display: flex; align-items: center; gap: 10px; font-size: 0.75rem;">
                            <div style="background: ${color}; width: 16px; height: 16px; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff;"><i data-lucide="${icon}" style="width:10px; height:10px;"></i></div>
                            <div style="width: 120px; color: #d1d5db; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${c.name}</div>
                            <div style="flex: 1; background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                                <div style="background: ${color}; width: ${c.percentage}%; height: 100%; border-radius: 3px;"></div>
                            </div>
                            <div style="color: #9ca3af; width: 35px; text-align: right;">${c.count}</div>
                            <div style="color: #fff; width: 25px; text-align: right;">${c.percentage}%</div>
                        </div>`;
                    }).join('');
                }
            }

            if(window.lucide) {
                window.lucide.createIcons();
            }
        }
    } catch (err) {
        console.error("Failed to fetch dashboard stats", err);
    }
});
