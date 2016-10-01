//post directive
(function(){
	angular.module('donkidik')
		.directive('postDir', function() {
			return {
		    	restrict: 'E',
		    	scope: {
		    		post: '=data'
		    	},
		    	replace: 'true',
		     	templateUrl: '/static/angular/templates/post.html',
		     	controller: function($scope, postService){

								$scope.posts = [];
								$scope.spots = [];
								//$scope.uid = null;
								$scope.create_post_type = ''
								$scope.selected_post_type = 'general';
								$scope.new_post_error = '';

								$scope.get_posts = function(uid, pid){
									$scope.posts = [];
									postService.get_posts(uid, pid).then(function(res){
										if (res.success) {
											$scope.posts = res.posts;
											$scope.posts_loaded = true;
										}
										else {
											//TODO: replace loading with error message
											alert('Error getting posts...');
										}
									});
								};

								$scope.reload_post_comments = function(post) {
									postService.reload_post_comments(post.post_id).then(function(res){
										if (res.success) {
											post.comments = res.comments;
										}
										else {
											alert('Error reloading post comments');
										}
									});
								};

								$scope.post_comment = function(post){
									if (!post.comm_text)
										return;

									var txt = post.comm_text;
									postService.post_comment(post.post_id, txt).then(function(){
										$scope.reload_post_comments(post);
										post.comm_text = '';
									});
								};

								$scope.delete_post = function(post){
									
									if (!confirm('Sure?'))
										return;

									postService.delete_post(post.post_id).then(function(res){
										if (res.success) {
											for (var i=0; i<$scope.posts.length; i++) {
												if ($scope.posts[i].post_id == post.post_id) {
													$scope.posts.splice(i, 1);
													break;
												}
											}
										}
										else {
											alert('Error deleting post');
										}
									});
								};

								$scope.post_upvote = function(post,uid){
									postService.post_upvote(post.post_id).then(function(res){
										if (res.status=='OK'){
											post.score += res.change_score;
											post.author.score = Math.max(post.author.score+res.change_score,0)
											if (res.change_score == -1){ // was previously upvoted. cancel the upvote
												post.is_upvoted = false;
												var i = post.upvotes.indexOf(res.uid);
												if (i >-1) post.upvotes.splice(i,1); //was already upvoted. cancel the previous upvote
												else alert('mismatch between post.upvotes and res.change_score');
												//TODO: remove else clause
											}
											else{ //increase score
												if (res.change_score > 1){
													var i = post.downvotes.indexOf(res.uid);
													if (i >-1){
														post.downvotes.splice(i,1); // delete previous downvote
														post.is_downvoted = false;
													}
													else alert('mismatch between post.downvotes and res.change_score');
													//TODO: remove else clause
												}
												post.upvotes.push(res.uid)
												post.is_upvoted = true;
											}
										}
										else{
											// TODO communicate this to UI
											if (res.error) alert(res.error);
											else alert("Service failed!");
										}
									});
								};

								$scope.post_downvote = function(post){
									postService.post_downvote(post.post_id).then(function(res){
										if (res.status=='OK'){
											post.score += res.change_score;
											post.author.score = Math.max(post.author.score+res.change_score,0)
											if (res.change_score == 1){ // was previously downvoted. cancel the downvote
												post.is_downvoted = false;
												var i = post.downvotes.indexOf(res.uid);
												if (i >-1) post.downvotes.splice(i,1); //was already downvoted. cancel the previous downvote
												else alert('mismatch between post.downvotes and res.change_score');
												//TODO: remove else clause
											}
											else{ //reduced score
												if (res.change_score < -1){
													var i = post.upvotes.indexOf(res.uid);
													if (i >-1){
														post.upvotes.splice(i,1); // delete previous upvote
														post.is_upvoted = false;
													}
													else alert('mismatch between post.upotes and res.change_score');
													//TODO: remove else clause
												}
												post.downvotes.push(res.uid)
												post.is_downvoted = true;
											}
										}
										else{
											// TODO communicate this to UI
											if (res.error) alert(res.error);
											else alert("Service failed!");
										}
									});
								};
							},
		    	link: function(scope, elem, attr){
		    		if (attr.uid || attr.pid){
		    			scope.get_posts(attr.uid, attr.pid);
		    		}
		    		//scope.post = scope.data;
				}
			  };
		});
})();
//time-ago directive
(function(){
	angular.module('donkidik')
		.directive('timeAgo', function() {
			return {
		    	restrict: 'E',
		    	scope: {
		    				
		    				taDate:'=postdate',
		    				taTime:'=posttime'
		    	},
		    	replace: 'true',
		     	template: '<div class="time">[[time_msg]]</div>',
		    	link: function(scope, elem, attr){
		    		scope.time_msg = 'not set';
			      	var 	month_time = 30*24*60*60,
			      			day_time = 24*60*60,
			      			hour_time = 3600,
			      			post_date = ("0" + scope.taDate[0]).substr(-2,2) + '/' + ("0" + scope.taDate[1]).substr(-2,2) + '/' + String(scope.taDate[2]).substr(-2,2)
			      			post_time = ("0" + scope.taTime[0]).substr(-2,2) + ':' + ("0" + scope.taTime[1]).substr(-2,2);
			      	if ( attr.seconds > month_time ) scope.time_msg = post_date + " at " + post_time; //more than a month
			      	else if ( attr.seconds > day_time ){ // more than a day
			      		var days = Math.floor( attr.seconds / day_time);
			      		if (days == 1) scope.time_msg = "yesterday at" + post_time;
			      		if (6 <= days <=8 ) scope.time_msg = "about a week ago";
			      		else scope.time_msg = days + " days ago at " + post_time;
			      	}
			      	else if ( attr.seconds > hour_time){
			      		var hours = Math.floor(attr.seconds / hour_time);
			      		if (hours == 1) scope.time_msg = "about an hour ago";
			      		else scope.time_msg = "about " + hours + " hours ago";
			      	}
			      	else if ( attr.seconds > 60){
			      		var minutes = Math.floor(attr.seconds / 60);
			      		if (minutes == 1) scope.time_msg = "about a minute ago";
			      		else scope.time_msg = "about " + minutes + " minutes ago";
			      	}
			      	else{
			      		if (attr.seconds == 1) scope.time_msg = "about a second ago";
			      		else scope.time_msg = "about " + attr.seconds + " seconds ago";
			      	}
			    }
			  };
		});
})();