document.addEventListener('DOMContentLoaded', async () => {
    const user = await requireAuth();
    if (!user) return;

    // Display User info in Nav
    document.getElementById('nav-name').textContent = user.name;
    const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    document.getElementById('nav-avatar').textContent = initials;

    const container = document.getElementById('profile-container');
    const viewHeader = document.getElementById('view-header');
    const editHeader = document.getElementById('edit-header');
    
    document.getElementById('btn-edit-mode').addEventListener('click', () => { currentEditTab = 'basic'; renderEditMode(); });
    document.getElementById('btn-view-mode').addEventListener('click', () => renderViewMode());

    const gridStyle = `display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 20px; max-width: 1300px; margin-left: auto; margin-right: auto;`;
    const editGridStyle = `display: grid; grid-template-columns: 250px 1fr; gap: 20px; max-width: 1000px; margin: 0 auto;`; 
    const cardStyle = `background: rgba(2, 12, 6, 0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 16px; position: relative; display: flex; flex-direction: column;`;
    const cardTitleStyle = `color: #fff; font-size: 0.95rem; font-weight: 600; margin: 0 0 16px 0; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;`;

    const rowStyle = `display: grid; grid-template-columns: 130px 1fr; gap: 8px; font-size: 0.75rem; align-items: start; margin-bottom: 10px;`;
    const labelColStyle = `display:flex; align-items:center; gap:6px; color:#9ca3af;`;
    const valColStyle = `color:#fff; line-height: 1.4;`;

    // Mock data based on user
    const profileData = {
        name: user.name,
        role: user.role,
        email: user.email,
        username: user.email.split('@')[0],
        memberSince: "10 Sep 2026",
        regDate: "10 Sep 2026, 11:24 AM",
        lastLogin: "3 Oct 2026, 6:45 PM",
        dob: "2007-03-24",
        gender: "Male",
        mobile: "+91 98765 43210",
        location: "Kota, Rajasthan, India",
        bio: "BCA student | Aspiring Full-Stack Developer | Interested in AI, Web Development and Technology.",
        course: "Bachelor of Computer Applications (BCA)",
        semester: "2nd Semester",
        enrollment: "BCA2026XXXX",
        dept: "Computer Applications",
        session: "2026 - 2029",
        institute: "Institution Name (e.g. MCU)"
    };

    let currentEditTab = 'basic';

    window.switchEditTab = function(tab) {
        currentEditTab = tab;
        renderEditMode();
    }

    function renderViewMode() {
        viewHeader.style.display = 'flex';
        editHeader.style.display = 'none';

        container.innerHTML = `
            <div style="${gridStyle}">
                
                <!-- Profile Overview -->
                <div style="${cardStyle}">
                    <div style="display: flex; gap: 16px; align-items: center; height: 100%;">
                        <div style="width: 80px; height: 80px; border-radius: 50%; background: #00D261; color: #041209; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; position: relative; flex-shrink:0;">
                            ${initials}
                            <div style="position: absolute; bottom: 0; right: 0; background: #041209; border: 1px solid rgba(255,255,255,0.2); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; color: #fff; cursor: pointer;">
                                <i data-lucide="camera" style="width:12px; height:12px;"></i>
                            </div>
                        </div>
                        <div style="flex: 1;">
                            <h2 style="color: #fff; margin: 0 0 6px 0; font-size: 1.2rem;">${profileData.name}</h2>
                            <span style="background: rgba(0, 210, 97, 0.15); color: #00D261; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; display: inline-flex; align-items: center; gap: 4px; margin-bottom: 8px;"><i data-lucide="user" style="width:12px; height:12px;"></i> ${profileData.role}</span>
                            <div style="display:flex; flex-direction:column; gap:4px; color:#9ca3af; font-size:0.75rem;">
                                <span style="display:flex; align-items:center; gap:6px;"><i data-lucide="mail" style="width:12px; height:12px;"></i> ${profileData.email}</span>
                                <span style="display:flex; align-items:center; gap:6px;"><i data-lucide="calendar" style="width:12px; height:12px;"></i> Member since ${profileData.memberSince}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Account Information -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Account Details</h3>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="user" style="width:14px; height:14px; color:#3b82f6;"></i> Full Name</div>
                        <div style="${valColStyle}">${profileData.name}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="at-sign" style="width:14px; height:14px; color:#3b82f6;"></i> Username</div>
                        <div style="${valColStyle}">${profileData.username}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="mail" style="width:14px; height:14px; color:#10b981;"></i> Email</div>
                        <div style="${valColStyle}; display:flex; justify-content:space-between; align-items:center;">
                            <span style="overflow:hidden; text-overflow:ellipsis;">${profileData.email}</span>
                            <span style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 2px 6px; border-radius: 10px; font-size: 0.65rem;"><i data-lucide="check" style="width:8px; height:8px;"></i> Verified</span>
                        </div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="shield" style="width:14px; height:14px; color:#f59e0b;"></i> Account Type</div>
                        <div style="${valColStyle}">${profileData.role}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="calendar" style="width:14px; height:14px; color:#8b5cf6;"></i> Registered</div>
                        <div style="${valColStyle}">${profileData.regDate}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="clock" style="width:14px; height:14px; color:#ec4899;"></i> Last Login</div>
                        <div style="${valColStyle}">${profileData.lastLogin}</div>
                    </div>
                </div>

                <!-- Personal Details -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Personal Details <button style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:#9ca3af; padding:2px 8px; border-radius:4px; font-size:0.7rem; cursor:pointer; display:flex; align-items:center; gap:4px;" onclick="switchEditTab('basic')"><i data-lucide="edit-2" style="width:10px; height:10px;"></i> Edit</button></h3>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="calendar" style="width:14px; height:14px; color:#ef4444;"></i> Date of Birth</div>
                        <div style="${valColStyle}">${profileData.dob}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="users" style="width:14px; height:14px; color:#10b981;"></i> Gender</div>
                        <div style="${valColStyle}">${profileData.gender}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="smartphone" style="width:14px; height:14px; color:#0ea5e9;"></i> Mobile</div>
                        <div style="${valColStyle}">${profileData.mobile}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="map-pin" style="width:14px; height:14px; color:#f59e0b;"></i> Location</div>
                        <div style="${valColStyle}">${profileData.location}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="file-text" style="width:14px; height:14px; color:#8b5cf6; margin-top:2px;"></i> Bio</div>
                        <div style="${valColStyle}">${profileData.bio}</div>
                    </div>
                </div>

                <!-- Academic Information -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Academic Info <button style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:#9ca3af; padding:2px 8px; border-radius:4px; font-size:0.7rem; cursor:pointer; display:flex; align-items:center; gap:4px;" onclick="switchEditTab('academic')"><i data-lucide="edit-2" style="width:10px; height:10px;"></i> Edit</button></h3>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="graduation-cap" style="width:14px; height:14px; color:#0ea5e9;"></i> Course</div>
                        <div style="${valColStyle}">${profileData.course}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="book-open" style="width:14px; height:14px; color:#8b5cf6;"></i> Semester</div>
                        <div style="${valColStyle}">${profileData.semester}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="hash" style="width:14px; height:14px; color:#10b981;"></i> Enrollment</div>
                        <div style="${valColStyle}">${profileData.enrollment}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="building" style="width:14px; height:14px; color:#3b82f6;"></i> Department</div>
                        <div style="${valColStyle}">${profileData.dept}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="calendar" style="width:14px; height:14px; color:#64748b;"></i> Session</div>
                        <div style="${valColStyle}">${profileData.session}</div>
                    </div>
                    <div style="${rowStyle}">
                        <div style="${labelColStyle}"><i data-lucide="library" style="width:14px; height:14px; color:#f59e0b;"></i> Institute</div>
                        <div style="${valColStyle}">${profileData.institute}</div>
                    </div>
                </div>

                <!-- Preferences -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Preferences <button style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:#9ca3af; padding:2px 8px; border-radius:4px; font-size:0.7rem; cursor:pointer; display:flex; align-items:center; gap:4px;" onclick="switchEditTab('preferences')"><i data-lucide="edit-2" style="width:10px; height:10px;"></i> Edit</button></h3>
                    <div style="${rowStyle} align-items:center;">
                        <div style="${labelColStyle}"><i data-lucide="globe" style="width:14px; height:14px; color:#3b82f6;"></i> Language</div>
                        <div style="${valColStyle}">English</div>
                    </div>
                    <div style="${rowStyle} align-items:center;">
                        <div style="${labelColStyle}"><i data-lucide="moon" style="width:14px; height:14px; color:#8b5cf6;"></i> Theme</div>
                        <div style="${valColStyle}">Dark</div>
                    </div>
                    <div style="${rowStyle} align-items:center;">
                        <div style="${labelColStyle}"><i data-lucide="message-square" style="width:14px; height:14px; color:#10b981;"></i> Answer Style</div>
                        <div style="${valColStyle}">Detailed Explanation</div>
                    </div>
                    <div style="${rowStyle} align-items:center;">
                        <div style="${labelColStyle}"><i data-lucide="link" style="width:14px; height:14px; color:#0ea5e9;"></i> Source Links</div>
                        <div style="${valColStyle}">
                            <div style="width:30px; height:16px; background:#00D261; border-radius:10px; position:relative;">
                                <div style="width:12px; height:12px; background:#fff; border-radius:50%; position:absolute; top:2px; right:2px;"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Security & Access -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Security</h3>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; font-size:0.75rem;">
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="lock" style="width:14px; height:14px; color:#64748b;"></i> Password</div>
                        <button onclick="switchEditTab('security')" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#fff; padding:4px 10px; border-radius:4px; font-size:0.7rem; cursor:pointer;">Change</button>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; font-size:0.75rem;">
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="shield-check" style="width:14px; height:14px; color:#0ea5e9;"></i> 2FA Auth</div>
                        <button style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#fff; padding:4px 10px; border-radius:4px; font-size:0.7rem; cursor:pointer;">Enable</button>
                    </div>
                    
                    <div style="margin-top: auto; padding: 10px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color:#ef4444; font-weight:600; font-size:0.75rem;">Delete Account</div>
                        </div>
                        <button style="background:transparent; border:1px solid rgba(239, 68, 68, 0.5); color:#ef4444; padding:4px 10px; border-radius:4px; font-size:0.7rem; cursor:pointer;">Delete</button>
                    </div>
                </div>
            </div>
        `;
        if (window.lucide) window.lucide.createIcons({root: container});
    }

    function renderEditMode() {
        viewHeader.style.display = 'none';
        editHeader.style.display = 'flex';

        const inputStyle = `width: 100%; padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; color: #fff; font-size: 0.85rem; outline: none; margin-top: 6px; transition: border 0.2s;`;
        const labelStyle = `display: block; color: #9ca3af; font-size: 0.75rem;`;
        
        const tabStyle = (tab) => currentEditTab === tab 
            ? `background: rgba(0, 210, 97, 0.1); color: #00D261; border: 1px solid rgba(0, 210, 97, 0.2); padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px;`
            : `color: #9ca3af; border: 1px solid transparent; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s;`;

        let rightContent = '';

        if (currentEditTab === 'basic') {
            rightContent = `
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Basic Information</h3>
                    <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 20px;">
                        <div style="width: 60px; height: 60px; border-radius: 50%; background: #00D261; color: #041209; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold;">
                            ${initials}
                        </div>
                        <div>
                            <button style="background:transparent; border:1px solid rgba(0,210,97,0.3); color:#00D261; padding:6px 12px; border-radius:4px; font-size:0.75rem; cursor:pointer; display:flex; gap:6px; align-items:center; margin-bottom:6px;"><i data-lucide="upload" style="width:14px; height:14px;"></i> Upload Photo</button>
                            <div style="font-size:0.7rem; color:#6b7280;">JPG, PNG (Max 2MB)</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div><label style="${labelStyle}">Full Name <span style="color:#ef4444">*</span></label><input type="text" value="${profileData.name}" style="${inputStyle}"></div>
                        <div>
                            <label style="${labelStyle}">Email Address</label>
                            <input type="email" value="${profileData.email}" disabled style="${inputStyle} opacity: 0.5; cursor: not-allowed;">
                        </div>
                        <div><label style="${labelStyle}">Date of Birth</label><input type="date" value="${profileData.dob}" style="${inputStyle}"></div>
                        <div>
                            <label style="${labelStyle}">Gender</label>
                            <select style="${inputStyle}">
                                <option value="Male" ${profileData.gender === 'Male' ? 'selected' : ''}>Male</option>
                                <option value="Female" ${profileData.gender === 'Female' ? 'selected' : ''}>Female</option>
                                <option value="Other" ${profileData.gender === 'Other' ? 'selected' : ''}>Other</option>
                            </select>
                        </div>
                        <div><label style="${labelStyle}">Mobile Number</label><input type="text" value="${profileData.mobile}" style="${inputStyle}"></div>
                        <div><label style="${labelStyle}">Location</label><input type="text" value="${profileData.location}" style="${inputStyle}"></div>
                        <div style="grid-column: span 2;"><label style="${labelStyle}">Bio / About You</label><textarea style="${inputStyle} height: 80px; resize:none;">${profileData.bio}</textarea></div>
                    </div>
                </div>
            `;
        } else if (currentEditTab === 'academic') {
            rightContent = `
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Academic Information</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div style="grid-column: span 2;"><label style="${labelStyle}">Course Name</label><input type="text" value="${profileData.course}" style="${inputStyle}"></div>
                        <div>
                            <label style="${labelStyle}">Semester / Year</label>
                            <select style="${inputStyle}">
                                <option value="1st Semester">1st Semester</option>
                                <option value="2nd Semester" selected>2nd Semester</option>
                                <option value="3rd Semester">3rd Semester</option>
                                <option value="4th Semester">4th Semester</option>
                                <option value="5th Semester">5th Semester</option>
                                <option value="6th Semester">6th Semester</option>
                            </select>
                        </div>
                        <div><label style="${labelStyle}">Enrollment / Roll Number</label><input type="text" value="${profileData.enrollment}" style="${inputStyle}"></div>
                        <div><label style="${labelStyle}">Department</label><input type="text" value="${profileData.dept}" style="${inputStyle}"></div>
                        <div><label style="${labelStyle}">Academic Session</label><input type="text" value="${profileData.session}" style="${inputStyle}"></div>
                        <div style="grid-column: span 2;"><label style="${labelStyle}">Institute Name</label><input type="text" value="${profileData.institute}" style="${inputStyle}"></div>
                    </div>
                </div>
            `;
        } else if (currentEditTab === 'preferences') {
            rightContent = `
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Platform Preferences</h3>
                    <div style="display: flex; flex-direction: column; gap: 20px;">
                        <div>
                            <label style="${labelStyle} margin-bottom:6px;">Default Chat Language</label>
                            <select style="${inputStyle}">
                                <option value="en">English (Default)</option>
                                <option value="hi">Hindi</option>
                                <option value="es">Spanish</option>
                            </select>
                            <div style="font-size:0.7rem; color:#6b7280; margin-top:4px;">The AI will try to reply in this language initially.</div>
                        </div>
                        <div>
                            <label style="${labelStyle} margin-bottom:6px;">UI Theme</label>
                            <select style="${inputStyle}">
                                <option value="dark">Dark Theme (Recommended)</option>
                                <option value="light">Light Theme</option>
                                <option value="system">System Default</option>
                            </select>
                        </div>
                        <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 16px;">
                            <label style="display:flex; justify-content:space-between; align-items:center; cursor:pointer;">
                                <div>
                                    <div style="color:#fff; font-size:0.85rem;">Show Source References</div>
                                    <div style="color:#9ca3af; font-size:0.75rem;">AI will attach document links below answers.</div>
                                </div>
                                <div style="width:36px; height:20px; background:#00D261; border-radius:10px; position:relative;">
                                    <div style="width:16px; height:16px; background:#fff; border-radius:50%; position:absolute; top:2px; right:2px;"></div>
                                </div>
                            </label>
                        </div>
                        <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 16px;">
                            <label style="display:flex; justify-content:space-between; align-items:center; cursor:pointer;">
                                <div>
                                    <div style="color:#fff; font-size:0.85rem;">Email Notifications</div>
                                    <div style="color:#9ca3af; font-size:0.75rem;">Receive live updates via email.</div>
                                </div>
                                <div style="width:36px; height:20px; background:rgba(255,255,255,0.1); border-radius:10px; position:relative;">
                                    <div style="width:16px; height:16px; background:#9ca3af; border-radius:50%; position:absolute; top:2px; left:2px;"></div>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>
            `;
        } else if (currentEditTab === 'security') {
            rightContent = `
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Change Password</h3>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div><label style="${labelStyle}">Current Password</label><input type="password" placeholder="Enter current password" style="${inputStyle}"></div>
                        <div><label style="${labelStyle}">New Password</label><input type="password" placeholder="Create a new password" style="${inputStyle}"></div>
                        <div><label style="${labelStyle}">Confirm New Password</label><input type="password" placeholder="Retype new password" style="${inputStyle}"></div>
                        <div style="margin-top: 10px;">
                            <button style="background:rgba(59, 130, 246, 0.1); border:1px solid rgba(59, 130, 246, 0.3); color:#3b82f6; padding:8px 16px; border-radius:6px; font-size:0.8rem; cursor:pointer;">Update Password</button>
                        </div>
                    </div>
                </div>
            `;
        }

        container.innerHTML = `
            <div style="${editGridStyle}">
                <!-- Left Sidebar Navigation for Edit Mode -->
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div onclick="switchEditTab('basic')" style="${tabStyle('basic')}">
                        <i data-lucide="user" style="width:16px; height:16px;"></i> Basic Info
                    </div>
                    <div onclick="switchEditTab('academic')" style="${tabStyle('academic')}">
                        <i data-lucide="graduation-cap" style="width:16px; height:16px;"></i> Academic Info
                    </div>
                    <div onclick="switchEditTab('preferences')" style="${tabStyle('preferences')}">
                        <i data-lucide="settings" style="width:16px; height:16px;"></i> Preferences
                    </div>
                    <div onclick="switchEditTab('security')" style="${tabStyle('security')}">
                        <i data-lucide="lock" style="width:16px; height:16px;"></i> Security
                    </div>
                </div>

                <!-- Right Content Area -->
                <div style="display: flex; flex-direction: column; gap: 20px;">
                    
                    ${rightContent}

                    <!-- Footer Actions -->
                    <div style="display:flex; justify-content:flex-end; gap:12px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 16px;">
                        <button onclick="document.getElementById('btn-view-mode').click()" style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:#e5e7eb; padding:8px 16px; border-radius:6px; font-size:0.8rem; cursor:pointer;">Cancel</button>
                        <button style="background:#00D261; border:none; color:#041209; padding:8px 20px; border-radius:6px; font-size:0.85rem; font-weight:600; cursor:pointer; display:flex; gap:6px; align-items:center;"><i data-lucide="save" style="width:16px; height:16px;"></i> Save Changes</button>
                    </div>

                </div>
            </div>
        `;
        
        if(!document.getElementById('compact-focus-style')) {
            document.head.insertAdjacentHTML('beforeend', '<style id="compact-focus-style">input:focus, select:focus, textarea:focus { border-color: #00D261 !important; }</style>');
        }

        if (window.lucide) window.lucide.createIcons({root: container});
    }

    renderViewMode();
});
